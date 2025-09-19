# -*- coding: utf-8 -*-
"""
管道编排：扫描→抽取→打分→归档→报告
"""
from pathlib import Path
from typing import List
from tqdm import tqdm
from .config import Config
        # ^^^^^^ keep relative imports
from .scanner import scan_dir, FileRecord
from .extractors import extract_pdf_text, extract_code_stats, extract_image_meta, extract_data_meta, safe_read_text
from .rules import score_record
from .organizer import organize
from .reporter import write_inventory, write_summary, write_readme
from .utils import log

def _extract_features(records: List[FileRecord], cfg: Config, max_bytes: int):
    for r in tqdm(records, desc="抽取特征"):
        if r.ext == ".pdf":
            r.text_sample = extract_pdf_text(r.path, max_bytes)
        elif r.ext in [".txt", ".md", ".rst"]:
            r.text_sample = safe_read_text(r.path, max_bytes)
        elif r.ext in cfg.categories.get("CODE", {}).get("exts", []):
            r.code_stats = extract_code_stats(r.path, max_bytes)
            r.text_sample = (r.text_sample or "") + " " + " ".join(
                [k for k,v in r.code_stats.items() for _ in range(v) if isinstance(v,int)]
            )
        elif r.ext in cfg.categories.get("FIGURE", {}).get("exts", []):
            r.image_meta = extract_image_meta(r.path)
        elif r.ext in cfg.categories.get("DATA", {}).get("exts", []):
            r.data_meta = extract_data_meta(r.path, r.ext, max_bytes)
        else:
            pass

def _score_all(records: List[FileRecord], cfg: Config):
    for r in tqdm(records, desc="规则打分"):
        score_record(r, cfg)

def run_pipeline(root: str, out_dir: str, config_path: str, mode: str,
                 max_bytes: int, dry_run: bool, profile: str):
    log("加载配置")
    cfg = Config(config_path)

    log("开始扫描目录")
    records = scan_dir(root)

    log("提取多模态轻量特征")
    _extract_features(records, cfg, max_bytes)

    log("应用规则打分与分类")
    _score_all(records, cfg)

    log("写出报告与清单")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    write_inventory(records, out_dir)
    write_summary(records, out_dir)
    write_readme(records, out_dir, templates_dir=str(Path(__file__).parent / "templates"))

    log("归档文件")
    organize(records, cfg, out_dir=out_dir, mode=mode, dry_run=dry_run)

    log("完成 ✅")
