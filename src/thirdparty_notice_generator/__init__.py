import sys
from datetime import timedelta
from pathlib import Path

from fucache import FuCache

from thirdparty_notice_generator.cargo import Cargo
from thirdparty_notice_generator.nuget import Nuget
from thirdparty_notice_generator.py import PyProject
from thirdparty_notice_generator.template import HEADER

one_month = timedelta(weeks=4)
month_sec = int(one_month.total_seconds())
FuCache.init("thirdparty_notice_generator", expiration_sec=month_sec)


def cli():
    if len(sys.argv) < 2:
        print("Usage: thirdparty-notice-generator <projectfile> [<outputfile>]")
        exit()
    proj = sys.argv[1]
    output = None
    if len(sys.argv) > 2:
        output = sys.argv[2]

    main(proj, output)


def main(project: str, output: str = None):
    p = Path(project)
    match p.suffix:
        case ".csproj" | ".sln":
            n = Nuget(p)
        case ".toml" if p.name == "pyproject.toml":
            n = PyProject(p)
        case ".toml" if p.name == "Cargo.toml":
            n = Cargo(p)
        case _:
            print(f"{project}: Unsupported project type")
            return

    notice, missing_list = n.export_third_party_notice()

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(HEADER)
            f.write(notice)
    else:
        print(notice)

    if missing_list:
        print()
        print("Failed to get infomation following packages.")
        print("\n".join(missing_list))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: thirdparty_notice_generator <projectfile> [<outputfile>]")
        exit()
    proj = sys.argv[1]
    output = None
    if len(sys.argv) > 2:
        output = sys.argv[2]

    main(proj, output)
