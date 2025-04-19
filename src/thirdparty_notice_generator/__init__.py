import sys
from pathlib import Path

from thirdparty_notice_generator.nuget import Nuget


def main(project: str, output: str = None):
    p = Path(project)
    match p.suffix:
        case ".csproj" | ".sln":
            n = Nuget(p)
        case _:
            print(f"{project}: Unsupported project type")
            return

    notice, missing_list = n.export_third_party_notice()

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(notice)
    else:
        print(notice)

    if missing_list:
        print()
        print("Failed to get infomation following packages.")
        print("\n".join(missing_list))


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: thirdparty_notice_generator <projectfile> [<outputfile>]")
        exit()
    proj = sys.argv[1]
    output = None
    if len(sys.argv) > 2:
        output = sys.argv[2]

    main(proj, output)
