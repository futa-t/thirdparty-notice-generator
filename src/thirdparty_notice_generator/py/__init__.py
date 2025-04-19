import json
import re
import tomllib
from pathlib import Path
from urllib import request

from thirdparty_notice_generator import licenses
from thirdparty_notice_generator.template import NOTICE


class Spec:
    def __init__(self, data: dict):
        self.id = data.get("name")
        self.version = data.get("version")
        self.authors = data.get("author")
        self.copyright = data.get("author")
        self.license = data.get("license") or data.get("license_expression")
        self.license_url = None
        self.repository = None
        source = data.get("project_urls", {}).get("Source", "")
        if "github" in source:
            self.repository = source

        if not self.repository:
            homepage = data.get("project_urls", {}).get("Homepage", "")
            if "github" in homepage:
                self.repository = homepage


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

        dependencies = data["project"].get("dependencies", [])
        self.dependencies = list(map(extract_package_name, dependencies))

    def export_third_party_notice(self) -> tuple[str, list[str]]:
        notice = ""
        missing_list = []
        for package in self.dependencies:
            print(package, end=" ")
            try:
                notice += PyProject.create_notice(package)
                print("[Success]")
            except Exception as e:
                missing_list.append(package)
                print("[Failed]")
                print(e)
        return notice, missing_list

    @staticmethod
    def get_package_data(package_name: str) -> Spec | None:
        url = f"https://pypi.org/pypi/{package_name}/json"
        try:
            with request.urlopen(url) as res:
                data = json.loads(res.read())
                return Spec(data["info"])
        except Exception:
            return None

    @staticmethod
    def create_notice(package_name: str) -> str | None:
        spec = PyProject.get_package_data(package_name)
        if not spec:
            return

        if r := spec.repository:
            license_text = licenses.github.get_license_text(r)

        license_text = license_text or licenses.spdx.get_license_text(spec.license)
        if not license_text:
            raise
        return NOTICE.format(
            packagename=spec.id,
            version=spec.version,
            licensename=spec.license,
            projecturl=spec.repository,
            licensetext=license_text,
        )


if __name__ == "__main__":
    import sys

    p = PyProject(sys.argv[1])
    # print(p.export_third_party_notice())
    print(PyProject.create_notice("pyperclip"))
