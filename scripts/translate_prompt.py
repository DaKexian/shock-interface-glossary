# -*- coding: utf-8 -*-
"""生成翻译提示词：把命中的术语和规则拼成一段可直接使用的 prompt。

用法：
  python translate_prompt.py --text 原文.txt --out prompt.md
  python translate_prompt.py --text 原文.txt --max-terms 40
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lookup import load, patterns  # noqa: E402

TEMPLATE = """# 翻译任务

把下面这段英文学术文本翻译成中文。

## 术语（必须遵守）

{glossary}

## 用词规则

1. 上表 confidence 为「高」「中」的词，必须使用给定译名；同一术语全篇一致。
2. confidence 为「低」「未定」的词，保留英文，首次出现处加中文括注；不要自己另造译名。
3. 表外专业名词：保留英文，首次出现处加中文括注（如无把握，直接保留英文）。
4. spike = 尖钉、bubble = 气泡，不得互换；shock 首选「激波」，「冲击波」只作通俗异名。
5. 不合并不同概念；原文有歧义时保留英文并注明。
6. 长句按中文语序重组，不逐词硬译；公式、符号、单位、引文编号原样保留。

## 原文

{text}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--out")
    ap.add_argument("--max-terms", type=int, default=60)
    args = ap.parse_args()

    text = Path(args.text).read_text(encoding="utf-8", errors="ignore")
    rows = [r for r in load() if r["status"] == "active" and r["en_norm"]]
    rows.sort(key=lambda r: -len(r["en_norm"]))

    hits = []
    for r in rows:
        n = len(patterns(r["en"]).findall(text))
        if n:
            hits.append((n, r))
    hits.sort(key=lambda x: (-x[0], -len(x[1]["en"])))
    # 去掉被更长命中词条包含的短词，避免同一处重复列词
    kept = []
    for n, r in hits:
        low = r["en"].lower()
        if any(low != o["en"].lower() and low in o["en"].lower() for _, o in hits):
            continue
        kept.append((n, r))
    hits = kept[:args.max_terms]

    lines = []
    for n, r in hits:
        zh = r["zh_main"]
        if r["confidence"] in ("低", "未定"):
            zh = f"（保留英文）{zh}"
        alt = r["zh_alt"].strip()
        alt_txt = f"（备选：{alt}）" if alt and alt != r["zh_main"] else ""
        lines.append(f"- {r['en']} = {zh}{alt_txt}  [出现 {n} 次，{r['confidence']}]")
    if not lines:
        lines.append("（本文未命中术语表任何词条）")

    prompt = TEMPLATE.format(glossary="\n".join(lines), text=text)
    if args.out:
        Path(args.out).write_text(prompt, encoding="utf-8")
        print(f"已写入 {args.out}（命中 {len(hits)} 条术语）")
    else:
        print(prompt)


if __name__ == "__main__":
    main()
