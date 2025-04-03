import zipfile
from datetime import date
from pathlib import Path

import pypinyin
import requests


URL = "https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_chengyu.txt"
OUT_DIR = Path("dist")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def download_chengyu(url: str) -> list[str]:
    resp = requests.get(url)
    resp.raise_for_status()
    return [line.split("\t")[0] for line in resp.text.splitlines() if line.strip()]


def write_main_dict(path: Path):
    content = """\
# Rime dict
---
name: luna_pinyin_packs
version: "1.0"
sort: original
use_preset_vocabulary: false
import_tables:
  - thuocl_chengyu
...
"""
    path.write_text(content, encoding="utf-8")


def write_schema(path: Path):
    content = """\
# Rime schema
schema:
  schema_id: luna_pinyin_packs

translator:
  dictionary: luna_pinyin_packs
  packs:
    - thuocl_chengyu
"""
    path.write_text(content, encoding="utf-8")


def write_chengyu_dict(entries: list[str], path: Path):
    today = date.today().isoformat()
    with path.open("w", encoding="utf-8") as f:
        f.write(f"""# Rime dict
---
name: thuocl_chengyu
version: "{today}"
sort: original
use_preset_vocabulary: false
...\n
""")
        for word in sorted(set(entries)):
            word = word.strip()
            f.write(f"{word}\t{pypinyin.lazy_pinyin(word)}\t100\n")


def create_zip(files: list[Path], zip_path: Path):
    with zipfile.ZipFile(zip_path, "w") as zf:
        for file in files:
            zf.write(file, arcname=file.name)


if __name__ == "__main__":
    words = download_chengyu(URL)
    main_dict = OUT_DIR / "luna_pinyin_packs.dict.yaml"
    schema_file = OUT_DIR / "luna_pinyin_packs.schema.yaml"
    chengyu_file = OUT_DIR / "thuocl_chengyu.dict.yaml"

    write_main_dict(main_dict)
    write_schema(schema_file)
    write_chengyu_dict(words, chengyu_file)
