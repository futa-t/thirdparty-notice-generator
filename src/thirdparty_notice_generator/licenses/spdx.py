import sys
from urllib import request

from fucache import FuCache

LICENSE_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/text/{identifier}.txt"


def get_license_text_with_cache(identifier: str) -> str | None:
    try:
        if text := FuCache.load_cache(identifier):
            return text.decode()

        text = get_license_text(identifier)
        FuCache.save_cache(identifier, text.encode())
        return text
    except Exception:
        return None


def get_license_text(identifier: str) -> str | None:
    try:
        url = LICENSE_URL.format(identifier=identifier)
        with request.urlopen(url) as res:
            text = res.read()
            return text.decode()
    except Exception:
        return None


def main():
    if len(sys.argv) > 1:
        identifier = sys.argv[1]
    else:
        identifier = input("License > ")

    if license := get_license_text(identifier):
        with open(f"LICENSE-{identifier}.txt", "w", encoding="utf-8") as f:
            f.write(license)
            print(license)
    else:
        print(identifier, "is not found.")


if __name__ == "__main__":
    main()
