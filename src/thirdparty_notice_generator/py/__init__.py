import json
import re
import tomllib
from pathlib import Path
from urllib import request

from fucache import FuCache

from thirdparty_notice_generator import licenses
from thirdparty_notice_generator.base import PackageBase
from thirdparty_notice_generator.template import NOTICE


class PySpec(PackageBase):
    def __init__(self, package_name: str):
        data = self.get_package_data(package_name)

        self._package_name = data.get("name", "")
        self._version = data.get("version", "")
        self._authors = data.get("author", "")
        self._copyright = data.get("author", "")
        self._license = data.get("license", "") or data.get("license_expression", "")
        self._license_url = None
        self._repository = ""

        source = data.get("project_urls", {}).get("Source", "")
        if "github" in source:
            self._repository = source

        if not self._repository:
            self._repository = data.get("project_urls", {}).get("Homepage", "")

        license_text = licenses.github.get_license_text(self._repository)
        self._license_text = license_text or licenses.spdx.get_license_text_with_cache(self._license) or ""

    def get_package_data(self, package_name: str) -> dict:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with request.urlopen(url) as res:
            data = json.loads(res.read())
            return data["info"]

    @property
    def package_name(self):
        return self._package_name

    @property
    def version(self) -> str:
        return self._version

    @property
    def author(self) -> str:
        return self._author

    @property
    def copyright(self) -> str:
        return self._copyright

    @property
    def license_name(self) -> str:
        return self._license_name

    @property
    def license_text(self) -> str:
        return self._license_text

    @license_text.setter
    def license_text(self, value):
        self._license_text = value

    @property
    def repository(self) -> str:
        return self._repository

    @property
    def notice(self):
        return NOTICE.format(
            packagename=self.package_name,
            version=self.version,
            licensename=self.license_text,
            projecturl=self.repository,
            licensetext=self.license_text,
        )


def extract_package_name(requirement: str) -> str:
    match = re.match(r"^([a-zA-Z0-9_.\-]+)", requirement)
    return match.group(1) if match else None


class PyProject:
    def __init__(self, pyproject: Path | str):
        self.proj = Path(pyproject).expanduser()
        if self.proj.is_dir():
            self.proj = self.proj / "pyproject.toml"
        if not self.proj.exists():
            raise Exception(f"{pyproject}: pyproject.toml is not found")

        with self.proj.open("rb") as f:
            data = tomllib.load(f)

        self.dependencies = data["project"].get("dependencies", [])

    def export_third_party_notice(self) -> tuple[str, list[str]]:
        notice = ""
        missing_list = []
        for package_name in self.dependencies:
            print(package_name, end=" ")
            try:
                notice += self.create_notice(package_name)
                print("[Success]")
            except Exception as e:
                missing_list.append(package_name)
                print("[Failed]")
                print(e)
        return notice, missing_list

    def create_notice(self, package_name: str) -> str:
        if cache := FuCache.load_cache(package_name):
            print("[Using Cache]", end="")
            return cache.decode()

        spec = PySpec(extract_package_name(package_name))

        FuCache.save_cache(package_name, spec.notice.encode())
        return spec.notice
