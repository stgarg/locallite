#!/usr/bin/env python3
"""Utility script to export an embedding model to ONNX for the benchmark harness.

Usage (from repo root or any directory):
    python scripts/export_bge_model.py --hf-model BAAI/bge-small-en-v1.5 \
        --out-dir models/bge-small-en-v1.5

If dependencies are missing it will print an install hint. This script is idempotent:
- Skips export if model.onnx already exists unless --force is passed.

We intentionally keep this narrow (feature-extraction task) to avoid
pulling in unnecessary complexity.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REQUIRED = ["transformers", "optimum", "onnx"]  # onnxruntime already in base reqs


def check_deps():
    missing = []
    for m in REQUIRED:
        try:
            __import__(m)
        except Exception:
            missing.append(m)
    if missing:
        print(
            "[export] Missing packages: " + ", ".join(missing) + "\n"
            "Install dev dependencies (includes export extras):\n"
            "    pip install -r ai-gateway/requirements-dev.txt\n"
            "Or minimal set:\n"
            "    pip install transformers optimum onnx\n"
        )
        sys.exit(2)


def run_export(hf_model: str, tmp_dir: Path):
    cmd = [
        sys.executable,
        "-m",
        "optimum.exporters.onnx",
        "--model",
        hf_model,
        "--task",
        "feature-extraction",
        str(tmp_dir),
    ]
    print("[export] Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Export embedding model to ONNX")
    parser.add_argument("--hf-model", default="BAAI/bge-small-en-v1.5", help="Hugging Face model id")
    parser.add_argument(
        "--out-dir", default="models/bge-small-en-v1.5", help="Target directory (relative to repo root if not absolute)"
    )
    parser.add_argument("--force", action="store_true", help="Re-export even if model.onnx already exists")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = repo_root / args.out_dir

    model_file = out_dir / "model.onnx"
    if model_file.exists() and not args.force:
        print(f"[export] {model_file} already exists; skipping (use --force to re-export)")
        return

    check_deps()

    with tempfile.TemporaryDirectory() as td:
        tmp_dir = Path(td) / "onnx_export"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        run_export(args.hf_model, tmp_dir)

        # Copy artifacts
        out_dir.mkdir(parents=True, exist_ok=True)
        primary = tmp_dir / "model.onnx"
        if not primary.exists():
            # Fallback: look for any .onnx
            onnx_files = list(tmp_dir.glob("*.onnx"))
            if not onnx_files:
                print("[export] No ONNX file produced; aborting")
                sys.exit(1)
            primary = onnx_files[0]
        shutil.copy2(primary, model_file)
        # Optional helpful extras (ignore if missing)
        for extra in ["config.json", "tokenizer.json", "tokenizer.model", "vocab.txt"]:
            src = tmp_dir / extra
            if src.exists():
                shutil.copy2(src, out_dir / extra)

    print(f"[export] Export complete: {model_file}")
    print("[export] Contents:")
    for p in sorted(out_dir.iterdir()):
        print("   ", p.name)


if __name__ == "__main__":  # pragma: no cover
    main()
