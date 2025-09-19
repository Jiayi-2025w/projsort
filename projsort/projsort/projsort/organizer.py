# -*- coding: utf-8 -*-
"""
归档：copy/move/link；去重；命名冲突处理
"""
import shutil
from pathlib import Path
from .utils import safe_mkdir, file_hash

def organize(records, cfg, out_dir: str, mode: str = None, dry_run: bool = False):
    mode = mode or cfg.organize.get("mode_default", "copy")
    sorted_root = Path(out_dir) / "_sorted"
    index_root = Path(out_dir) / "_index"
    safe_mkdir(sorted_root)
    safe_mkdir(index_root)

    dedup = cfg.organize.get("dedup_by_hash", True)
    algo = cfg.organize.get("hash_algo", "md5")
    seen = {}

    for rec in records:
        target_sub = cfg.target_dir_for(rec.label)
        cat_dir = sorted_root / target_sub
        safe_mkdir(cat_dir)

        if dedup:
            try:
                h = file_hash(rec.path, algo=algo)
                rec.file_hash = h
                if h in seen:
                    link_path = index_root / f"{rec.rel_path.name}.{h[:8]}"
                    if not dry_run:
                        if link_path.exists():
                            link_path.unlink()
                        # 索引软链（Windows 可能需要管理员权限）
                        try:
                            link_path.symlink_to(seen[h])
                        except Exception:
                            # 回退：复制一个占位索引文件（记录来源）
                            link_path.write_text(f"DUPLICATE OF: {seen[h]}\n", encoding="utf-8")
                    continue
                else:
                    seen[h] = cat_dir / rec.path.name
            except Exception:
                pass

        target = cat_dir / rec.path.name
        if target.exists():
            stem = target.stem
            suffix = target.suffix
            h8 = (rec.file_hash[:8] if rec.file_hash else "dup")
            target = cat_dir / f"{stem}__{h8}{suffix}"

        if dry_run:
            continue

        if mode == "copy":
            shutil.copy2(rec.path, target)
        elif mode == "move":
            shutil.move(str(rec.path), target)
        elif mode == "link":
            try:
                target.symlink_to(rec.path)
            except Exception:
                shutil.copy2(rec.path, target)
        else:
            shutil.copy2(rec.path, target)
