import json
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET

from fucache import FuCache

from thirdparty_notice_generator import licenses
from thirdparty_notice_generator.base import PackageBase
from thirdparty_notice_generator.template import NOTICE


class Nuspec(PackageBase):
    def __init__(self, package_path: Path):
        self.path = package_path
        if len(nuspecs := list(package_path.glob("*.nuspec"))) > 0:
            self.nuspec = nuspecs[0]
        else:
            raise FileNotFoundError(f"{package_path}: not found .nuspec")

        root = ET.parse(self.nuspec).getroot()
        ns = root.tag.removesuffix("package")
        meta = root.find(f"{ns}metadata")

        def findtext(tag):
            return meta.findtext(f"{ns}{tag}")

        self._package_name = findtext("id")
        self._version = findtext("version")
        self._authors = findtext("authors")
        self._copyright = findtext("copyright")
        self._license_name = findtext("license[@type='expression']")
        self.license_url = findtext("licenseUrl")
        self.project_url = findtext("projectUrl")

        try:
            self._repository = meta.find(ns + "repository").attrib.get("url").removesuffix(".git")
        except Exception:
            self._repository = ""

        license_text = licenses.directory.get_license_text(self.path)
        license_text = license_text or licenses.github.get_license_text(self.repository)
        self._license_text = license_text or licenses.spdx.get_license_text_with_cache(self._license_name) or ""

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
    def notice(self) -> str:
        return NOTICE.format(
            packagename=self.package_name,
            version=self.version,
            licensename=self.license_name,
            projecturl=self.repository,
            licensetext=self.license_text,
        )


class Nuget:
    def __init__(self, project_path: str):
        self.proj = Path(project_path).expanduser()
        if self.proj.is_file():
            self.proj = self.proj.parent
        self.use_spdx_license_list = False

    def export_third_party_notice(self) -> tuple[str, list[str]]:
        project_assets_json = self.get_project_assets(self.proj)
        package_list = self.get_package_list(project_assets_json)

        notice = ""
        missing_list = []
        for package_name in package_list.keys():
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
        g = self.get_global_package_dir()
        p = g / package_name.lower()
        n = package_name.replace("/", "_")
        if cache := FuCache.load_cache(n):
            print("[Using Cache]", end="")
            return cache.decode()

        nuspec = Nuspec(p)
        FuCache.save_cache(n, nuspec.notice.encode())
        return nuspec.notice

    def get_project_assets(self, project_root: Path):
        f = project_root / "obj" / "project.assets.json"
        if not f.exists():
            raise Exception("project.assets.json is not found")
        return f

    def get_global_package_dir(self) -> Path:
        if (p := Path.home() / ".nuget" / "packages").exists():
            return p

        res = subprocess.run(["dotnet", "nuget", "locals", "global-packages", "--list"], stdout=subprocess.PIPE)
        return res.stdout.decode().split(" ", 1)[-1].strip()

    def get_package_list(self, project_assets_json: Path | str) -> list[str] | None:
        with open(project_assets_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("libraries", {})
