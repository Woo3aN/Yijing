# hexagrams.json 数据格式说明

## 文件位置

`src/data/hexagrams.json`

## 整体结构

一个 JSON 数组，包含 64 个对象，按《周易》通行本王弼注本的卦序排列（1乾～64未济）。

## 单卦数据结构

```json
{
  "number": 1,
  "binary": "111111",
  "name": "乾",
  "pinyin": "qián",
  "symbol": "䷀",
  "upper_trigram": "乾",
  "lower_trigram": "乾",
  "judgment": "元亨利贞。",
  "tuan_zhuan": "《彖》曰：大哉乾元，万物资始，乃统天。云行雨施，品物流形。大明终始，六位时成。时乘六龙以御天。乾道变化，各正性命。保合太和，乃利贞。首出庶物，万国咸宁。",
  "xiang_zhuan": "《象》曰：天行健，君子以自强不息。",
  "lines": [
    {
      "position": 1,
      "label": "初九",
      "text": "潜龙勿用。",
      "xiang": "《象》曰：潜龙勿用，阳在下也。"
    }
  ]
}
```

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `number` | int | 卦序，1-64 |
| `binary` | string | 6位二进制，"1"=阳(--), "0"=阴(- -) |
| `name` | string | 卦名，如"乾" |
| `pinyin` | string | 拼音，如"qián" |
| `symbol` | string | Unicode 卦符，如"䷀" |
| `upper_trigram` | string | 上卦（上三爻组成的八卦名） |
| `lower_trigram` | string | 下卦（下三爻组成的八卦名） |
| `judgment` | string | 卦辞 — 整卦的核心判断 |
| `tuan_zhuan` | string | 《彖传》— 对卦辞的阐释 |
| `xiang_zhuan` | string | 《象传》大象 — 卦的整体象征 |
| `lines` | array | 6个爻的对象数组 |

### lines[] 数组项结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `position` | int | 爻位，从下往上 1-6 |
| `label` | string | 传统爻名：初九/九二/九三/九四/九五/上九 或 初六/六二/六三/六四/六五/上六 |
| `text` | string | 爻辞 |
| `xiang` | string | 《象传》小象 — 对该爻的阐释 |

## binary 字段约定

- `binary[0]` = 最下面的爻（初爻，position=1）
- `binary[5]` = 最上面的爻（上爻，position=6）
- 例："111111" 表示全部为阳爻（乾卦）
- 例："000000" 表示全部为阴爻（坤卦）

## 起卦时的查找逻辑

程序启动时根据 hexagrams.json 构建两个查找表：

1. **按卦序查**：`{number → hexagram_dict}` — O(1) 查找
2. **按二进制查**：`{"111111" → 1, "000000" → 2, ...}` — 由爻值推卦序

起卦算法根据六个爻值生成 binary 字符串，查表得卦序，再取完整数据。

## 文本来源

《周易》通行本（王弼注本），为公共领域古典文献。
参考来源：维基文库（zh.wikisource.org/wiki/周易）

## 数据编写注意事项

1. 64 卦必须完整，缺一不可
2. 每卦的 lines 数组必须有且只有 6 项
3. 爻的 label 要严格遵循命名规则：
   - 阳爻(1)：初九/九二/九三/九四/九五/上九
   - 阴爻(0)：初六/六二/六三/六四/六五/上六
4. binary 要与 lines 的实际阴阳一致
5. symbol 使用 Unicode 卦符 (U+4DC0–U+4DFF)
