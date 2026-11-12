# -*- coding: utf-8 -*-
"""查词：在文本中查找术语表命中的词。

用法：
  python lookup.py --text 文件路径
  echo "some english text" | python lookup.py
"""
import argparse
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "terms.tsv"
COLS = ["id", "en", "en_norm", "zh_main", "zh_alt", "pos", "domain", "definition_zh",
        "usage_zh", "pitfall_zh", "source_type", "source_ref", "confidence", "status", "attest", "note"]


def load():
    if not DATA.exists():
        sys.exit(f"术语表不存在: {DATA}")
    lines = DATA.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        p = line.split("\t")
        if len(p) < len(header):
            p += [""] * (len(header) - len(p))
        rows.append(dict(zip(header, p)))
    return rows


def patterns(en):
    """英文术语 → 容忍连字符（含 en/em dash）/空格/大小写/常见词尾变化的匹配"""
    parts = [re.escape(x) for x in re.split(r"[\s\-–—]+", en.strip()) if x]
    body = r"[\s\-–—]+".join(parts)
    return re.compile(r"(?<![A-Za-z])" + body + r"(?:s|es|ed|ing)?(?![A-Za-z])", re.IGNORECASE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text")
    ap.add_argument("--min-confidence", default="未定")
    args = ap.parse_args()

    text = Path(args.text).read_text(encoding="utf-8", errors="ignore") if args.text else sys.stdin.read()
    rows = [r for r in load() if r["status"] == "active" and r["en_norm"]]
    rows.sort(key=lambda r: -len(r["en_norm"]))

    hits = []
    for r in rows:
        n = len(patterns(r["en"]).findall(text))
        if n:
            hits.append((r, n))
    hits.sort(key=lambda x: (-x[1], -len(x[0]["en"])))

    if not hits:
        print("未命中术语表。建议：把新词用 add.py 补进词典。")
        return

    print(f"命中 {len(hits)} 条：\n")
    print("次数\t英文\t主译\t备选\t置信度\t领域")
    for r, n in hits:
        print(f"{n}\t{r['en']}\t{r['zh_main']}\t{r['zh_alt']}\t{r['confidence']}\t{r['domain']}")

    weak = [r for r, _ in hits if r["confidence"] in ("低", "未定")]
    if weak:
        print("\n注意：以下术语置信度低，翻译时保留英文：")
        for r in weak:
            print(f"  - {r['en']}（{r['confidence']}）{r['note']}")


if __name__ == "__main__":
    main()
