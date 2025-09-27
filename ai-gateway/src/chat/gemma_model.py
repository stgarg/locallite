"""Gemma 3n chat model integration skeleton."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

from chat.base import BaseChatModel, ChatGeneration
from core.router_types import UnifiedRequest

logger = logging.getLogger(__name__)


class GemmaChatModel(BaseChatModel):
    """ONNX-based text generation for Gemma 3n."""

    NUM_LAYERS = 30
    KEY_NAME_TEMPLATE = "past_key_values.{layer}.key"
    VALUE_NAME_TEMPLATE = "past_key_values.{layer}.value"
    PRESENT_KEY_TEMPLATE = "present.{layer}.key"
    PRESENT_VALUE_TEMPLATE = "present.{layer}.value"

    def __init__(self, model_id: str, model_path: str):
        super().__init__(model_id=model_id, model_path=model_path)
        self.decoder_session: Optional[ort.InferenceSession] = None
        self.embed_session: Optional[ort.InferenceSession] = None
        self.tokenizer: Optional[Tokenizer] = None
        self.providers: List[str] = []
        self.decoder_output_names: List[str] = []
        self.embed_output_names: List[str] = []
        self.eos_token_ids: Sequence[int] = (1, 106)  # From generation_config.json
        self.pad_token_id: int = 0
        self.max_context: int = 32768
        self.default_max_new_tokens: int = 256
        self.rng = np.random.default_rng()

    async def load(self) -> bool:
        try:
            tokenizer_path = os.path.join(self.model_path, "tokenizer.json")
            if not os.path.exists(tokenizer_path):
                raise FileNotFoundError(f"Tokenizer file not found: {tokenizer_path}")

            self.tokenizer = Tokenizer.from_file(tokenizer_path)
            logger.info("Loaded Gemma tokenizer (%s)", tokenizer_path)

            available = ort.get_available_providers()
            preferred = [
                "QNNExecutionProvider",
                "DmlExecutionProvider",
                "CPUExecutionProvider",
            ]
            providers = [p for p in preferred if p in available]
            if not providers:
                providers = ["CPUExecutionProvider"]

            # Load embedding projection model
            embed_model_file = os.path.join(
                self.model_path, "onnx", "embed_tokens_quantized.onnx"
            )
            if not os.path.exists(embed_model_file):
                raise FileNotFoundError(
                    f"Gemma embed_tokens ONNX not found: {embed_model_file}"
                )

            self.embed_session = ort.InferenceSession(embed_model_file, providers=providers)
            self.embed_output_names = [out.name for out in self.embed_session.get_outputs()]
            logger.info(
                "Gemma embedding model loaded with providers: %s", self.embed_session.get_providers()
            )

            # Load decoder model
            decoder_model_file = os.path.join(
                self.model_path, "onnx", "decoder_model_merged_q4.onnx"
            )
            if not os.path.exists(decoder_model_file):
                raise FileNotFoundError(
                    f"Gemma decoder ONNX not found: {decoder_model_file}"
                )

            self.decoder_session = ort.InferenceSession(decoder_model_file, providers=providers)
            self.providers = self.decoder_session.get_providers()
            self.decoder_output_names = [out.name for out in self.decoder_session.get_outputs()]
            logger.info("Gemma decoder loaded with providers: %s", self.providers)

            self.is_loaded = True
            return True

        except Exception as exc:
            logger.error("Failed to load Gemma model: %s", exc)
            self.is_loaded = False
            self.decoder_session = None
            self.embed_session = None
            self.tokenizer = None
            return False

    async def unload(self) -> None:
        self.decoder_session = None
        self.embed_session = None
        self.tokenizer = None
        self.is_loaded = False

    async def generate(self, request: UnifiedRequest) -> ChatGeneration:
        if not self.is_loaded or not self.decoder_session or not self.embed_session or not self.tokenizer:
            raise RuntimeError("GemmaChatModel not loaded")

        messages: Sequence[Dict[str, Any]] = request.content.get("messages", [])
        max_tokens: Optional[int] = request.content.get("max_tokens")
        temperature: float = float(request.content.get("temperature", 0.7) or 0.0)
        top_p: float = float(request.content.get("top_p", 1.0) or 1.0)
        stop_sequences = self._normalize_stop_sequences(request.content.get("stop"))

        prompt_text = self._build_prompt_from_messages(messages)
        encoding = self.tokenizer.encode(prompt_text)
        input_ids = encoding.ids
        prompt_token_count = len(input_ids)

        if prompt_token_count >= self.max_context:
            raise ValueError(
                f"Prompt too long ({prompt_token_count} tokens). Max context {self.max_context}."
            )

        max_new_tokens = int(max_tokens or self.default_max_new_tokens)
        if max_new_tokens <= 0:
            max_new_tokens = self.default_max_new_tokens

        logger.info(
            "Gemma prompt prepared (prompt_tokens=%s, max_new_tokens=%s, temp=%s, top_p=%s)",
            prompt_token_count,
            max_new_tokens,
            temperature,
            top_p,
        )

        # Prime decoder with full prompt
        past_key_values = self._init_past_key_values()
        total_length = prompt_token_count

        logits, past_key_values = self._run_decoder_step(
            input_token_ids=np.array([input_ids], dtype=np.int64),
            position_offset=0,
            past_key_values=past_key_values,
        )

        generated_ids: List[int] = []
        finish_reason = "stop"
        accumulated_text = ""

        for step in range(max_new_tokens):
            next_token_id = self._select_next_token(logits, temperature, top_p)
            generated_ids.append(int(next_token_id))

            if next_token_id in self.eos_token_ids:
                finish_reason = "stop"
                generated_ids.pop()  # Do not include EOS in final text
                break

            # Decode partial text to evaluate stop sequences
            partial_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
            truncated_text, stopped = self._apply_stop_sequences(partial_text, stop_sequences)
            accumulated_text = truncated_text
            if stopped:
                finish_reason = "stop"
                break

            total_length += 1
            if total_length >= self.max_context:
                finish_reason = "length"
                break

            logits, past_key_values = self._run_decoder_step(
                input_token_ids=np.array([[next_token_id]], dtype=np.int64),
                position_offset=prompt_token_count + len(generated_ids) - 1,
                past_key_values=past_key_values,
            )

        else:
            finish_reason = "length"
            accumulated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        if not accumulated_text:
            accumulated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        metadata: Dict[str, Any] = {
            "providers": self.providers,
            "stop_sequences": stop_sequences,
            "generated_tokens": len(generated_ids),
        }

        return ChatGeneration(
            text=accumulated_text.strip(),
            tokens=len(generated_ids),
            prompt_tokens=prompt_token_count,
            finish_reason=finish_reason,
            provider_used=self.providers[0] if self.providers else "unknown",
            metadata=metadata,
        )

    def _run_decoder_step(
        self,
        input_token_ids: np.ndarray,
        position_offset: int,
        past_key_values: Sequence[Tuple[np.ndarray, np.ndarray]],
    ) -> Tuple[np.ndarray, Sequence[Tuple[np.ndarray, np.ndarray]]]:
        """Run embedding + decoder for given token IDs and return logits and presents."""

        if not self.embed_session or not self.decoder_session:
            raise RuntimeError("Gemma sessions not initialised")

        embed_outputs = self.embed_session.run(
            self.embed_output_names,
            {"input_ids": input_token_ids},
        )

        inputs_embeds, per_layer_inputs = embed_outputs

        seq_len = input_token_ids.shape[1]
        position_ids = (
            np.arange(position_offset, position_offset + seq_len, dtype=np.int64)
            .reshape(1, seq_len)
        )

        decoder_inputs: Dict[str, np.ndarray] = {
            "inputs_embeds": inputs_embeds.astype(np.float32),
            "per_layer_inputs": per_layer_inputs.astype(np.float32),
            "position_ids": position_ids,
        }

        for layer_idx, (key_cache, value_cache) in enumerate(past_key_values):
            decoder_inputs[self.KEY_NAME_TEMPLATE.format(layer=layer_idx)] = key_cache
            decoder_inputs[self.VALUE_NAME_TEMPLATE.format(layer=layer_idx)] = value_cache

        outputs = self.decoder_session.run(self.decoder_output_names, decoder_inputs)
        output_map = dict(zip(self.decoder_output_names, outputs))

        logits = output_map["logits"][:, -1, :]  # [batch, vocab]

        next_past: List[Tuple[np.ndarray, np.ndarray]] = []
        for layer_idx in range(self.NUM_LAYERS):
            next_key = output_map[self.PRESENT_KEY_TEMPLATE.format(layer=layer_idx)]
            next_value = output_map[self.PRESENT_VALUE_TEMPLATE.format(layer=layer_idx)]
            next_past.append((next_key.astype(np.float32), next_value.astype(np.float32)))

        return logits, next_past

    def _init_past_key_values(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        empty = []
        for _ in range(self.NUM_LAYERS):
            zero_shape = (1, 2, 0, 256)
            empty.append(
                (
                    np.zeros(zero_shape, dtype=np.float32),
                    np.zeros(zero_shape, dtype=np.float32),
                )
            )
        return empty

    def _select_next_token(self, logits: np.ndarray, temperature: float, top_p: float) -> int:
        logits = logits[0].astype(np.float32)

        if temperature is None or temperature <= 0.0:
            return int(np.argmax(logits))

        adjusted_logits = logits / max(temperature, 1e-5)
        adjusted_logits -= np.max(adjusted_logits)
        probs = np.exp(adjusted_logits)
        probs /= np.sum(probs)

        if top_p is not None and 0 < top_p < 1.0:
            sorted_indices = np.argsort(probs)[::-1]
            sorted_probs = probs[sorted_indices]
            cumulative = np.cumsum(sorted_probs)
            cutoff = cumulative <= top_p
            if not np.any(cutoff):
                cutoff[0] = True
            filtered_indices = sorted_indices[cutoff]
            filtered_probs = sorted_probs[cutoff]
            filtered_probs /= np.sum(filtered_probs)
            choice = self.rng.choice(filtered_indices, p=filtered_probs)
            return int(choice)

        choice = self.rng.choice(len(probs), p=probs)
        return int(choice)

    def _normalize_stop_sequences(self, stop: Any) -> List[str]:
        if not stop:
            return []
        if isinstance(stop, str):
            return [stop]
        if isinstance(stop, Iterable):
            return [s for s in stop if isinstance(s, str)]
        return []

    def _apply_stop_sequences(
        self, text: str, stop_sequences: Sequence[str]
    ) -> Tuple[str, bool]:
        if not stop_sequences:
            return text, False
        for seq in stop_sequences:
            if seq and seq in text:
                return text.split(seq)[0], True
        return text, False

    def _build_prompt_from_messages(self, messages: List[Dict[str, Any]]) -> str:
        parts: List[str] = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            parts.append(f"<|{role}|>\n{content}<|end|>")
        parts.append("<|assistant|>\n")
        return "\n".join(parts)

    def health_check(self) -> Dict[str, Any]:
        base = super().health_check()
        base.update(
            {
                "providers": self.providers,
                "tokenizer_loaded": self.tokenizer is not None,
                "embed_loaded": self.embed_session is not None,
            }
        )
        return base
