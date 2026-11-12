---
name: shock-interface-glossary
description: '激波–界面不稳定性术语词典（RMI/RTI/ICF/激波反射/湍流混合）。翻译英文文献前先查表、按置信度使用译名、低置信保留英文、遇到新术语就地增补。用户说“翻译 / 术语 / 译名 / 中英对照 / 词典 / 这个词怎么翻”时使用。'
---

# 激波–界面不稳定性术语词典

面向 RMI / RTI / ICF / 激波反射 / 湍流混合方向的中英术语库。

- 主数据：`data/terms.tsv`（3543 条，active 2692）
- 搭配句：`data/collocations.tsv`
- 待裁决：`data/conflicts.tsv`（默认保留英文）

## 翻译流程

1. 查表：`python scripts/lookup.py --text <文件>`
2. 生成提示词：`python scripts/translate_prompt.py --text <文件> --out prompt.md`
3. 译后自检：把译文与词表一起发回模型，只问“逐条检查是否违例”，不要重译。

## 译名规则

| confidence | 用法 |
| --- | --- |
| 高 | 直接采用 `zh_main` |
| 中 | 采用 `zh_main`；上下文不符时用 `zh_alt`，或保留英文并首次括注 |
| 低 | 保留英文，首次出现处括注中文 |
| 未定 | 一律保留英文，不要自己补译名 |

硬规则（用户裁定，优先级最高）：

- **Richtmyer–Meshkov 保留英文**，中文统一写「RM 不稳定性」；首次出现可写「Richtmyer–Meshkov (RM) 不稳定性」，之后用 RM；
- **Atwood number = 阿特伍德数**（不是“阿特伍德比”）；`Atwood ratio` 才写“阿特伍德比”；
- **reshock = 反射激波**（备选“二次激波”）；
- `spike` = 尖钉、`bubble` = 气泡，RMI 语境下不得互换；
- `shock` 首选“激波”，“冲击波”只作通俗异名；
- 同一英文多义项时按 `domain` 列选，不要合并。

## 增词

```bash
python scripts/add.py --en "freeze-out" --zh "冻结" --alt "冻结态" \
  --domain 理论 --def "第二道激波后增长率归零的状态" \
  --source-type 中文文献 --source-ref "《…》p.7" --confidence 高
```

## 边界

- 只读 Zotero 库；不修改 `zotero.sqlite`、`storage/`；
- `data/conflicts.tsv` 里的条目不要自动裁决；
- 词典是活文档：翻译中发现新词或错译，就地 `add.py` 补上。
