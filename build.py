import re
import zipfile
from datetime import date
from pathlib import Path

import requests
from pypinyin import lazy_pinyin


OUT_DIR = Path("dist")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 分类名: {url, total}
SOURCE_CONFIG = {
    "chengyu": {
        "url": "https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_chengyu.txt",
        "total": 8421097,
    },
    "caijing": {
        "url": "https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_caijing.txt",
        "total": 8421097,
    },
    "diming": {
        "url": "https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_diming.txt",
        "total": 729008561,
    },
    "food": {
        "url": "https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_food.txt",
        "total": 729008561,
    },
    "animal": {
        "url": "https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_animal.txt",
        "total": 729008561,
    },
}


def fetch_entries(url: str) -> list[tuple[str, int]]:
    resp = requests.get(url)
    resp.raise_for_status()
    lines = [l.strip() for l in resp.text.splitlines(keepends=False) if l.strip()]
    result = []
    for line in lines:
        line = re.sub(r"[^\u4e00-\u9fff\s\d]", "", line)  # “”‘’
        w, c = line.strip().split("\t")
        w = w.strip()
        c = c.strip()
        if len(w) >= 2 and c.isdigit():
            result.append((w, int(c)))
    return result


def write_combined_dict(entries: list[tuple[str, int]], output: Path):
    today = date.today().isoformat()
    with output.open("w", encoding="utf-8") as f:
        f.write(f"""# Rime dict
---
name: thuocl_all
version: "{today}"
sort: original
use_preset_vocabulary: false
...
""")
        for word, freq in entries:
            pinyin = " ".join(lazy_pinyin(word))
            f.write(f"{word}\t{pinyin}\t50\n")


def write_main_schema_and_dict():
    (OUT_DIR / "luna_pinyin_packs.dict.yaml").write_text("""# Rime dict
---
name: luna_pinyin_packs
version: "1.0"
sort: original
use_preset_vocabulary: false
import_tables:
  - thuocl_all
...
""", encoding="utf-8")

    (OUT_DIR / "luna_pinyin_packs.schema.yaml").write_text("""# Rime schema
schema:
  schema_id: luna_pinyin_packs

translator:
  dictionary: luna_pinyin_packs
  packs:
    - thuocl_all
""", encoding="utf-8")


def create_zip(files: list[Path], zip_path: Path):
    with zipfile.ZipFile(zip_path, "w") as zf:
        for file in files:
            zf.write(file, arcname=file.name)


if __name__ == "__main__":
    all_entries = []

    for category, conf in SOURCE_CONFIG.items():
        entries = fetch_entries(conf["url"])
        total = conf["total"]
        for word, raw_freq in entries:
            percent = int(raw_freq / total * 1000)
            all_entries.append((word, percent))

    all_entries = sorted(set(all_entries))  # 去重排序

    dict_path = OUT_DIR / "thuocl_all.dict.yaml"
    write_combined_dict(all_entries, dict_path)

    write_main_schema_and_dict()

    create_zip(
        [dict_path,
         OUT_DIR / "luna_pinyin_packs.dict.yaml",
         OUT_DIR / "luna_pinyin_packs.schema.yaml"],
        Path("rime_extension_chengyu.zip")
    )
