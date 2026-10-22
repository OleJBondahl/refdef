"""Command line: `python -m refdef api` prints the public surface."""

import sys

from refdef._api import DOORS, render


def main(argv: list[str]) -> int:
    """Run the one command, `api`; any other argument is a usage error (exit 2)."""
    if argv != ["api"]:
        sys.stderr.write("usage: python -m refdef api\n")
        return 2
    sys.stdout.write(render(DOORS))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
