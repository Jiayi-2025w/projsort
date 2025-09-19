# -*- coding: utf-8 -*-
# 单文件运行入口（推荐）。用户只需在这里修改路径和若干开关项，然后直接运行即可。

# ========================= 用户可配置区（修改这里） =========================
ROOT_DIR   = r"/path/to/your/project"   # 要扫描与整理的项目根目录
OUT_DIR    = r"/path/to/output_dir"     # 输出目录：将生成 _sorted/、PROJECT_SUMMARY.md 等
MODE       = "copy"                      # copy / move / link
MAX_BYTES  = 1_000_000                   # 读取单文件的最大字节数（防卡）
DRY_RUN    = False                       # True：只生成报告清单，不实际移动/复制文件
CONFIG_YAML= "config/categories.yaml"    # 类目与规则配置
PROFILE    = None                        # 预留：行业 profile
# ==========================================================================

if __name__ == "__main__":
    from projsort.pipeline import run_pipeline
    print("[projsort] 运行配置：")
    print(f"  ROOT_DIR   = {ROOT_DIR}")
    print(f"  OUT_DIR    = {OUT_DIR}")
    print(f"  MODE       = {MODE}")
    print(f"  MAX_BYTES  = {MAX_BYTES}")
    print(f"  DRY_RUN    = {DRY_RUN}")
    print(f"  CONFIG_YAML= {CONFIG_YAML}")
    print(f"  PROFILE    = {PROFILE}")
    run_pipeline(
        root=ROOT_DIR,
        out_dir=OUT_DIR,
        config_path=CONFIG_YAML,
        mode=MODE,
        max_bytes=MAX_BYTES,
        dry_run=DRY_RUN,
        profile=PROFILE,
    )
