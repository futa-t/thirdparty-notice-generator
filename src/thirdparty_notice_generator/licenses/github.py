import json
import os
from urllib import request


def get_license_text(github_url: str, token: str = None) -> str | None:
    try:
        endpoint = (
            github_url.removesuffix(".git").replace("https://github.com", "https://api.github.com/repos") + "/license"
        )

        req = request.Request(endpoint)

        if token:
            req.headers = {"Accept": "application/vnd.github.v3+json", "Authorization": f"token {token}"}

        with request.urlopen(req) as res:
            json_text = res.read().decode()
            data = json.loads(json_text)

        if download_url := data.get("download_url"):
            with request.urlopen(download_url) as res:
                return res.read().decode()
    except Exception:
        return None


def get_rate_limit(token: str = None):
    endpoint = "https://api.github.com/rate_limit"
    req = request.Request(endpoint)

    if token:
        req.headers = {"Accept": "application/vnd.github.v3+json", "Authorization": f"token {token}"}

    try:
        with request.urlopen(req) as res:
            json_text = res.read().decode()
            data = json.loads(json_text)
            print(json.dumps(data, indent=4))
    except Exception as e:
        print(e)


if __name__ == "__main__":
    print(get_license_text(input("repository > "), os.getenv("GH_DEV_PAT")))
