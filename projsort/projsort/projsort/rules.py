# -*- coding: utf-8 -*-
"""
规则打分器：将多来源线索映射为各类目的分数 + 可解释理由
"""
from typing import Dict, List

def _score_init(categories: Dict[str, dict]) -> Dict[str, float]:
    return {c: 0.0 for c in categories.keys()}

def score_record(rec, cfg) -> None:
    W = cfg.weights
    categories = cfg.categories
    scores = _score_init(categories)
    reasons: List[str] = []

    # 1) 扩展名强先验
    ext = rec.ext
    for cat, meta in categories.items():
        if ext in [e.lower() for e in meta.get("exts", [])]:
            scores[cat] += W.get("ext", 1.0)
            reasons.append(f"[ext] {ext}→{cat}+{W.get('ext',1.0)}")

    # 2) 路径关键词
    rel = str(rec.rel_path).lower()
    for cat, kws in cfg.path_keywords.items():
        hit = [k for k in kws if k in rel]
        if hit:
            s = W.get("path", 0.6)
            scores[cat] += s
            reasons.append(f"[path] {','.join(hit)}→{cat}+{s}")

    # 3) 文本关键词
    txt = (rec.text_sample or "").lower()
    if txt:
        for cat, kws in cfg.text_keywords.items():
            cnt = sum(1 for k in kws if k.lower() in txt)
            if cnt > 0:
                s = W.get("text", 0.8) * min(cnt, 3) / 3.0
                scores[cat] += s
                reasons.append(f"[text] {cnt}kw→{cat}+{s:.2f}")

    # 4) 元信息：图片/数据
    if rec.image_meta:
        s = W.get("meta", 0.5)
        scores["FIGURE"] = scores.get("FIGURE", 0.0) + s
        reasons.append(f"[meta:img] {rec.image_meta.get('width','?')}x{rec.image_meta.get('height','?')}→FIGURE+{s}")
    if rec.data_meta:
        s = W.get("meta", 0.5)
        scores["DATA"] = scores.get("DATA", 0.0) + s
        reasons.append(f"[meta:data] columns→DATA+{s}")

    # 5) OTHER 轻微负偏置
    for cat in scores:
        if cat == "OTHER":
            scores[cat] += cfg.weights.get("default_bias_other", -0.3)

    # 6) 选择标签 + 置信度
    sorted_cat = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_cat, top_score = sorted_cat[0]
    sec_score = sorted_cat[1][1] if len(sorted_cat) > 1 else 0.0
    pos_sum = sum([max(v, 0.0) for v in scores.values()]) + 1e-6
    confidence = max(0.0, (top_score - sec_score) / pos_sum)

    if confidence < cfg.thresholds.get("maybe", 0.30):
        label = "OTHER"
    elif confidence < cfg.thresholds.get("accept", 0.45):
        label = top_cat
    else:
        label = top_cat

    rec.scores = scores
    rec.label = label
    rec.confidence = confidence
    rec.reasons = sorted(reasons)[:5]
