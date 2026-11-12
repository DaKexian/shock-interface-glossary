# -*- coding: utf-8 -*-
"""增词：往术语表追加一条记录（可反复运行，自动去重）。

用法：
  python add.py --en "freeze-out" --zh "冻结" --alt "冻结态" --domain 理论 \
      --def "第二道激波后增长率归零的状态" --source-type 中文文献 \
      --source-ref "《…》p.7" --confidence 高
"""
import argparse
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "terms.tsv"
HEADER = ["id", "en", "en_norm", "zh_main", "zh_alt", "pos", "domain", "definition_zh",
          "usage_zh", "pitfall_zh", "source_type", "source_ref", "confidence", "status", "attest", "note"]


def norm(s):
    s = re.sub(r"\s+", " ", s.lower().replace("-", " ")).strip()
    if len(s) > 3 and s.endswith("s") and not s.endswith("ss"):
        s = s[:-1]
    return s


def load_rows():
    if not DATA.exists():
        DATA.parent.mkdir(parents=True, exist_ok=True)
        DATA.write_text("\t".join(HEADER) + "\n", encoding="utf-8")
        return []
    lines = DATA.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    return [dict(zip(header, (l.split("\t") + [""] * len(header))[:len(header)])) for l in lines[1:] if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--en", required=True)
    ap.add_argument("--zh", required=True)
    ap.add_argument("--alt", default="")
    ap.add_argument("--pos", default="名词")
    ap.add_argument("--domain", default="")
    ap.add_argument("--def", dest="definition", default="")
    ap.add_argument("--source-type", default="通用")
    ap.add_argument("--source-ref", default="")
    ap.add_argument("--confidence", default="中", choices=["高", "中", "低", "未定"])
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    rows = load_rows()
    en_norm = norm(args.en)
    same = [r for r in rows if r["en_norm"] == en_norm]

    if any(r["zh_main"] == args.zh for r in same):
        print(f"已存在：{args.en} → {args.zh}（未改动）")
        return

    status = "active"
    note = args.note
    if same:
        status = "conflict"
        others = "；".join(f"{r['zh_main']}({r['confidence']})" for r in same)
        note = (note + f" 与已有译名冲突：{others}").strip()
        print(f"注意：{args.en} 已有 {others}，本次写入标为 conflict，请人工裁决。")

    ids = [int(r["id"][1:]) for r in rows if re.match(r"^T\d+$", r["id"])]
    new_id = f"T{(max(ids) + 1) if ids else 1:04d}"

    row = [new_id, args.en, en_norm, args.zh, args.alt, args.pos, args.domain, args.definition,
           "", "", args.source_type, args.source_ref, args.confidence, status, "手工增补", note]
    with open(DATA, "a", encoding="utf-8") as f:
        f.write("\t".join(row) + "\n")
    print(f"已添加：{new_id} {args.en} → {args.zh} [{args.confidence}/{status}]")


if __name__ == "__main__":
    main()
