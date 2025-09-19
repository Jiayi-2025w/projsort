# -*- coding: utf-8 -*-
"""
工具函数：安全IO、哈希、文本清洗、简易日志
"""
import hashlib
import os
import re
from pathlib import Path

def file_hash(path: Path, algo="md5", chunk=65536) -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()

def safe_mkdir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s

def norm_ext(name: str) -> str:
    return (Path(name).suffix or "").lower()

def human_bytes(n: int) -> str:
    for unit in ["B","KB","MB","GB","TB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"

def short_reason(reasons, topk=3):
    return "; ".join(reasons[:topk])

def log(msg: str):
    print(f"[projsort] {msg}")
