# -*- coding: utf-8 -*-
"""
轻量多模态特征抽取：
- PDF/文本：取少量片段（title/abstract 关键词探测）
- 代码：统计 import/def/class/#include/template 等关键词次数
- 图片：读尺寸/模式
- 数据：表头/形状（只窥探前几行）
"""
from pathlib import Path
from .utils import clean_text
from pdfminer.high_level import extract_text as pdf_extract_text
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound
from PIL import Image
import pandas as pd

def safe_read_text(path: Path, max_bytes: int) -> str:
    try:
        with open(path, "rb") as f:
            b = f.read(max_bytes)
        return clean_text(b.decode("utf-8", errors="ignore"))
    except Exception:
        return ""

def extract_pdf_text(path: Path, max_bytes: int) -> str:
    try:
        txt = pdf_extract_text(str(path)) or ""
        return clean_text(txt[:max_bytes])
    except Exception:
        return safe_read_text(path, max_bytes)

def extract_code_stats(path: Path, max_bytes: int) -> dict:
    txt = safe_read_text(path, max_bytes)
    stats = {}
    try:
        lexer = guess_lexer_for_filename(str(path), txt)
        stats["language"] = lexer.name
    except ClassNotFound:
        stats["language"] = "Unknown"
    for kw in ["import ", "def ", "class ", "#include", "template<", "using namespace"]:
        stats[kw.strip()] = txt.count(kw)
    stats["lines"] = txt.count("\n") + 1 if txt else 0
    return stats

def extract_image_meta(path: Path) -> dict:
    try:
        with Image.open(path) as im:
            w, h = im.size
            mode = im.mode
        return {"width": w, "height": h, "mode": mode}
    except Exception:
        return {}

def extract_data_meta(path: Path, ext: str, max_bytes: int) -> dict:
    meta = {}
    try:
        if ext in [".csv", ".tsv"]:
            sep = "," if ext == ".csv" else "\t"
            df = pd.read_csv(path, nrows=10, sep=sep)
            meta["columns"] = ",".join(map(str, df.columns.tolist()[:10]))
            meta["preview_rows"] = len(df)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(path, nrows=10)
            meta["columns"] = ",".join(map(str, df.columns.tolist()[:10]))
            meta["preview_rows"] = len(df)
        elif ext == ".json":
            txt = safe_read_text(Path(path), max_bytes)
            meta["json_snippet"] = txt[:200]
        else:
            pass
    except Exception:
        pass
    return meta
