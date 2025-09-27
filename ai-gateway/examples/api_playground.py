"""Simple interactive playground for the AI Gateway.
Run inside virtualenv after starting server (or let it start one in-process later).

Usage:
    python ai-gateway/examples/api_playground.py --host http://127.0.0.1:8000

Provides helper functions to call embeddings, chat, and model listing.
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap
from typing import List, Dict, Any

import requests


def pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def get_health(host: str):
    r = requests.get(f"{host}/health", timeout=10)
    print("# /health")
    print(pretty(r.json()))


def list_models(host: str):
    r = requests.get(f"{host}/v1/models", timeout=10)
    print("# /v1/models")
    print(pretty(r.json()))


def list_registry(host: str):
    r = requests.get(f"{host}/v1/models/registry", timeout=10)
    print("# /v1/models/registry")
    print(pretty(r.json()))


def embed(host: str, inputs: List[str]):
    payload = {"model": "bge-small-en-v1.5", "input": inputs if len(inputs) > 1 else inputs[0]}
    r = requests.post(f"{host}/v1/embeddings", json=payload, timeout=30)
    print("# /v1/embeddings")
    try:
        data = r.json()
    except Exception:
        print(r.text)
        return
    # Truncate embedding vectors for readability
    for item in data.get("data", []):
        emb = item.get("embedding", [])
        if isinstance(emb, list) and len(emb) > 12:
            item["embedding_preview"] = emb[:12]
            del item["embedding"]
    print(pretty(data))


def chat(host: str, prompt: str):
    payload = {
        "model": "gemma-3n-4b",
        "messages": [
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 64,
    }
    r = requests.post(f"{host}/v1/chat/completions", json=payload, timeout=60)
    print("# /v1/chat/completions")
    try:
        print(pretty(r.json()))
    except Exception:
        print(r.text)


def main():
    parser = argparse.ArgumentParser(description="AI Gateway API playground")
    parser.add_argument("--host", default="http://127.0.0.1:8000", help="Base host URL")
    parser.add_argument("--skip-chat", action="store_true", help="Skip chat example")
    args = parser.parse_args()

    banner = textwrap.dedent(
        f"""
        ===============================================
        AI Gateway Playground
        Host: {args.host}
        ===============================================
        """
    )
    print(banner)

    try:
        get_health(args.host)
        list_models(args.host)
        list_registry(args.host)
        embed(args.host, ["The quick brown fox jumps over the lazy dog."])
        embed(args.host, [
            "Short embedding sample.",
            "Another input to test batching logic.",
            "Third sentence to trigger provider selection paths.",
        ])
        if not args.skip_chat:
            chat(args.host, "Explain what an embedding vector is in one sentence.")
    except requests.ConnectionError as ce:
        print(f"Connection failed: {ce}\nIs the server running?")
        sys.exit(1)


if __name__ == "__main__":
    main()
