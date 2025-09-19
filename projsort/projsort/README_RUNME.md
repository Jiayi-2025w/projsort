# projsort (MVP)

## 安装
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## ✅ 最简单的用法：单文件运行
编辑 `run_projsort.py` 顶部的参数（尤其是 ROOT_DIR / OUT_DIR），然后：
```bash
python run_projsort.py
```

## 备选：命令行方式
```bash
python projsort_cli.py --root /path/to/your/project --out /path/to/output_dir --mode copy
```

可选参数：
- `--max-bytes`：抽取文本/表格预览的最大读入字节（默认 1MB）
- `--dry-run`：只生成报告清单，不执行拷贝/移动
- `--profile`：预留（后续行业词库/规则集）
