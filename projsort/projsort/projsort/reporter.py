# -*- coding: utf-8 -*-
"""
报告器：
- inventory.csv（清单）
- PROJECT_SUMMARY.md（统计、可读总览）
- README_AUTO.md（模板化生成）
"""
from pathlib import Path
import csv
from collections import Counter, defaultdict
from jinja2 import Environment, FileSystemLoader, select_autoescape
import matplotlib.pyplot as plt
from .utils import safe_mkdir, human_bytes, short_reason

def write_inventory(records, out_dir: str):
    p = Path(out_dir) / "inventory.csv"
    cols = ["rel_path", "size_bytes", "ext", "label", "confidence", "reasons", "hash"]
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in records:
            w.writerow([
                str(r.rel_path),
                r.size,
                r.ext,
                r.label,
                f"{r.confidence:.3f}",
                short_reason(r.reasons),
                r.file_hash
            ])

def _plot_category_bar(stats: Counter, out_dir: str):
    if not stats:
        return None
    fig_path = Path(out_dir) / "category_distribution.png"
    cats = list(stats.keys())
    vals = [stats[c] for c in cats]
    plt.figure()
    plt.bar(cats, vals)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()
    return fig_path

def write_summary(records, out_dir: str):
    out = Path(out_dir)
    safe_mkdir(out)

    total = len(records)
    sizes = sum([r.size for r in records])
    by_cat = Counter([r.label for r in records])
    fig_path = _plot_category_bar(by_cat, out_dir)

    lang_counter = Counter()
    for r in records:
        lang = r.code_stats.get("language") if r.code_stats else None
        if r.label == "CODE" and lang:
            lang_counter[lang] += 1

    md = Path(out_dir) / "PROJECT_SUMMARY.md"
    with open(md, "w", encoding="utf-8") as f:
        f.write("# Project Summary\n\n")
        f.write(f"- Files scanned: **{total}**\n")
        f.write(f"- Total size: **{human_bytes(sizes)}**\n\n")
        f.write("## Category Distribution\n\n")
        for c, v in by_cat.most_common():
            f.write(f"- {c}: {v}\n")
        if fig_path:
            f.write("\n![Category Distribution](category_distribution.png)\n")

        if lang_counter:
            f.write("\n## Code Languages (rough guess)\n\n")
            for l, v in lang_counter.most_common():
                f.write(f"- {l}: {v}\n")

        f.write("\n## Notes\n- 本报告由 projsort 自动生成；分类依据记录在 inventory.csv 的 reasons 字段中。\n")

def write_readme(records, out_dir: str, templates_dir: str):
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape()
    )
    tpl = env.get_template("readme.jinja2")

    by_cat = Counter([r.label for r in records])
    example_files = defaultdict(list)
    for r in records:
        if len(example_files[r.label]) < 3:
            example_files[r.label].append(str(r.rel_path))

    content = tpl.render(
        by_cat=by_cat,
        example_files=example_files,
    )
    (Path(out_dir) / "README_AUTO.md").write_text(content, encoding="utf-8")
