import json
import subprocess
import sys
from pathlib import Path


class Nuget:
    def __init__(self, project_path: str):
        self.proj = Path(project_path)
        if self.proj.is_file():
            self.proj = self.proj.parent
        self.use_spdx_license_list = False

    def export_third_party_notice(self, output_name: str = "ThirdPartyNotice.txt"):
        project_assets_json = self.get_project_assets(self.proj)
        package_list = self.get_package_list(project_assets_json)
        return package_list

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
            return list(data.get("libraries", {}).keys())


if __name__ == "__main__":
    p = Path(sys.argv[1])
    match p.suffix:
        case ".csproj" | ".sln":
            n = Nuget(p)
            print(n.export_third_party_notice())
