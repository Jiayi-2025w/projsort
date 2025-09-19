# -*- coding: utf-8 -*-
"""
命令行入口：解析参数 -> 调用pipeline执行全流程
"""
import argparse
from projsort.pipeline import run_pipeline

def build_parser():
    p = argparse.ArgumentParser(description="Project Auto-Organizer (MVP)")
    p.add_argument("--root", required=True, help="要扫描与整理的项目根目录")
    p.add_argument("--out", required=True, help="输出的归档目录（将创建/_sorted等）")
    p.add_argument("--mode", default=None, choices=["copy", "move", "link"],
                   help="归档方式，默认读取config.categories.yaml里的organize.mode_default")
    p.add_argument("--config", default="config/categories.yaml", help="类目与规则配置文件")
    p.add_argument("--max-bytes", type=int, default=1_000_000,
                   help="单文件读取上限字节（避免大文件卡死），默认1MB")
    p.add_argument("--dry-run", action="store_true", help="只生成报告与清单，不实际移动/拷贝")
    p.add_argument("--profile", default=None, help="预留：行业剖面（后续可加载专用词库）")
    return p

def main():
    args = build_parser().parse_args()
    run_pipeline(
        root=args.root,
        out_dir=args.out,
        config_path=args.config,
        mode=args.mode,
        max_bytes=args.max_bytes,
        dry_run=args.dry_run,
        profile=args.profile,
    )

if __name__ == "__main__":
    main()
