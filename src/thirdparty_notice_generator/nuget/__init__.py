import json
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET

from thirdparty_notice_generator import licenses
from thirdparty_notice_generator.template import NOTICE


class Nuspec:
    def __init__(self, package_path: Path):
        if len(nuspecs := list(package_path.glob("*.nuspec"))) > 0:
            self.nuspec = nuspecs[0]
        else:
            raise FileNotFoundError(f"{package_path}: not found .nuspec")

        root = ET.parse(self.nuspec).getroot()
        ns = root.tag.removesuffix("package")
        meta = root.find(f"{ns}metadata")

        def findtext(tag):
            return meta.findtext(f"{ns}{tag}")

        self.id = findtext("id")
        self.version = findtext("version")
        self.authors = findtext("authors")
        self.copyright = findtext("copyright")
        self.license = findtext("license[@type='expression']")
        self.license_url = findtext("licenseUrl")
        self.project_url = findtext("projectUrl")

        try:
            self.repository = meta.find(ns + "repository").attrib.get("url")
        except Exception:
            self.repository = None


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
        for name, value in package_list.items():
            print(name, end=" ")
            try:
                notice += self.create_notice(name, value["path"])
                print("[Success]")
            except Exception as e:
                missing_list.append(name)
                print("[Failed]")
                print(e)

        return notice, missing_list

    def create_notice(self, name, path):
        nuspec = self.get_nuspec(name)
        license_text = self.get_license_from_package(path)

        if nuspec.repository:
            license_text = license_text or licenses.github.get_license_text(nuspec.repository)

        license_text = license_text or licenses.spdx.get_license_text(nuspec.license)
        if not license_text:
            raise
        return NOTICE.format(
            packagename=nuspec.id,
            version=nuspec.version,
            licensename=nuspec.license,
            projecturl=nuspec.repository,
            licensetext=license_text,
        )

    def get_project_assets(self, project_root: Path):
        f = project_root / "obj" / "project.assets.json"
        if not f.exists():
            raise Exception("project.assets.json is not found")
        return f

    def get_global_package_dir(self) -> Path:
        p = Path("~/.nuget/packages").expanduser()
        if p.exists():
            return p

        res = subprocess.run(["dotnet", "nuget", "locals", "global-packages", "--list"], stdout=subprocess.PIPE)
        return res.stdout.decode().split(" ", 1)[-1].strip()

    def get_package_list(self, project_assets_json: Path | str) -> list[str] | None:
        with open(project_assets_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("libraries", {})

    def get_license_from_package(self, package_name: str) -> str | None:
        g = self.get_global_package_dir()
        p = g / package_name.lower()
        license_file = list(p.glob("license.txt", case_sensitive=False))
        if len(license_file) > 0:
            try:
                with license_file[0].open("r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(p)
                print(e)
                return None

    def get_nuspec(self, package_name: str) -> Nuspec:
        g = self.get_global_package_dir()
        p = g / package_name.lower()
        return Nuspec(p)
