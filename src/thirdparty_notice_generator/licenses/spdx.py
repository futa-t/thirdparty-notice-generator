from pathlib import Path
from urllib import request

LICENSE_CACHE_DIR = "~/.cache/licenses"
LICENSE_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/text/{identifier}.txt"


def create_cache_file_name(identifier: str) -> Path:
    cache_dir = Path(LICENSE_CACHE_DIR).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    return (cache_dir / identifier).with_suffix(".txt")


def get_license_text(identifier: str) -> str | None:
    try:
        if text := load_cache(identifier):
            return text
        url = LICENSE_URL.format(identifier=identifier)
        print(url)
        with request.urlopen(LICENSE_URL.format(identifier=identifier)) as res:
            text = res.read()
            cache = create_cache_file_name(identifier)
            with cache.open("wb") as f:
                f.write(text)
            return text.decode()
    except Exception:
        return None


def load_cache(identifier: str) -> str | None:
    p = Path(LICENSE_CACHE_DIR, identifier).expanduser().with_suffix(".txt")
    if not p.exists():
        return None

    try:
        with p.open("r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


if __name__ == "__main__":
    print(get_license_text(input("License > ")))
