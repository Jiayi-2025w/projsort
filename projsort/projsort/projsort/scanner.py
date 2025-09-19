# -*- coding: utf-8 -*-
"""
递归扫描：收集基础元数据
"""
from dataclasses import dataclass, field
from pathlib import Path
import os
from typing import List, Dict
from tqdm import tqdm
from .utils import norm_ext

@dataclass
class FileRecord:
    path: Path
    rel_path: Path
    ext: str
    size: int
    text_sample: str = ""
    code_stats: Dict[str, int] = field(default_factory=dict)
    image_meta: Dict[str, int] = field(default_factory=dict)
    data_meta: Dict[str, str] = field(default_factory=dict)
    scores: Dict[str, float] = field(default_factory=dict)
    label: str = "OTHER"
    confidence: float = 0.0
    reasons: list = field(default_factory=list)
    file_hash: str = ""

def scan_dir(root: str) -> List[FileRecord]:
    root_p = Path(root).resolve()
    files = []
    for dirpath, dirnames, filenames in os.walk(root_p):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fn in filenames:
            fp = Path(dirpath) / fn
            try:
                if not fp.is_file():
                    continue
                size = fp.stat().st_size
            except Exception:
                continue
            rec = FileRecord(
                path=fp,
                rel_path=fp.relative_to(root_p),
                ext=norm_ext(fn),
                size=size,
            )
            files.append(rec)
    for _ in tqdm(range(1), desc=f"扫描文件: {len(files)} 个"):
        pass
    return files
