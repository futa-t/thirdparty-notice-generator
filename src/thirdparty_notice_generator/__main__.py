import sys

from thirdparty_notice_generator import main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: thirdparty_notice_generator <projectfile> [<outputfile>]")
        exit()
    proj = sys.argv[1]
    output = None
    if len(sys.argv) > 2:
        output = sys.argv[2]

    main(proj, output)
