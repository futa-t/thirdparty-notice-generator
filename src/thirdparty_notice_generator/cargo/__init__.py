import json
import tomllib
from pathlib import Path
from urllib import request

from fucache import FuCache

from thirdparty_notice_generator import licenses
from thirdparty_notice_generator.base import PackageBase
from thirdparty_notice_generator.template import NOTICE


class CrateIO(PackageBase):
    def __init__(self, package_name: str, version: str):
        self._package_name = package_name
        self._version = version
        data = self.get_data().get("version") or {}

        self._authors = data.get("published_by", {}).get("name", "")
        self._copyright = self._authors

        self._license = data.get("license", "")
        self._license_url = None
        self._repository = data.get("repository", "")
        self._license_text = licenses.github.get_license_text(self._repository)

    def get_data(self) -> dict:
        cache_name = f"{self.package_name}_{self.version}.json"
        if cache := FuCache.load_cache(cache_name):
            print("[Using Cache]", end="")
            return json.loads(cache.decode())

        url = f"https://crates.io/api/v1/crates/{self.package_name}/{self.version}"
        with request.urlopen(url) as res:
            d = res.read()
            FuCache.save_cache(cache_name, d)
            data = json.loads(d)
            return data

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
        return self._license

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
            licensename=self.license_name,
            projecturl=self.repository,
            licensetext=self.license_text,
        )


class Cargo:
    def __init__(self, project_path: Path):
        data = tomllib.loads(project_path.read_text())
        self.dependencies = []
        for name, value in data.get("dependencies").items():
            match value:
                case str(s):
                    self.dependencies.append((name, s))
                case {"version": str(v), **_opts}:
                    self.dependencies.append((name, v))

    def export_third_party_notice(self) -> tuple[str, list[str]]:
        notice = ""
        missing_list = []

        for name, version in self.dependencies:
            package_name = f"{name}/{version}"
            print(name, version, end=" ")
            try:
                notice += self.create_notice(name, version)
                print("[Success]")
            except Exception as e:
                missing_list.append(package_name)
                print("[Failed]")
                print(e)

        return notice, missing_list

    def create_notice(self, name: str, version: str) -> str:
        package_name = f"{name}/{version}"
        if cache := FuCache.load_cache(package_name):
            print("[Using Cache]", end="")
            return cache.decode()

        spec = CrateIO(name, version)

        FuCache.save_cache(package_name, spec.notice.encode())
        return spec.notice
