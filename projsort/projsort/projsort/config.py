# -*- coding: utf-8 -*-
"""
配置加载与访问
"""
import yaml
from pathlib import Path

class Config:
    def __init__(self, path: str):
        self.path = Path(path)
        with open(self.path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        self.categories = cfg.get("categories", {})
        self.path_keywords = cfg.get("path_keywords", {})
        self.text_keywords = cfg.get("text_keywords", {})
        self.weights = cfg.get("weights", {})
        self.thresholds = cfg.get("thresholds", {})
        self.organize = cfg.get("organize", {})

    def ext_to_category_candidates(self):
        mapping = {}
        for cat, meta in self.categories.items():
            for e in meta.get("exts", []):
                mapping.setdefault(e.lower(), set()).add(cat)
        return mapping

    def target_dir_for(self, category: str) -> str:
        return self.categories.get(category, {}).get("target_dir", category.lower())
