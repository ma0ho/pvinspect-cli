from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path

import pvinspect as pv  # type: ignore
from docstring_parser.parser import parse  # type: ignore

from command import call_target, handle_result, setup_command


def init_parser() -> ArgumentParser:
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers()

    # preproc.stitching.locate_and_stitch_modules
    setup_command(
        pv.preproc.stitching.locate_and_stitch_modules,
        "preproc.stitching.locate_and_stitch_modules",
        subparsers,
    )

    return parser


if __name__ == "__main__":

    parser = init_parser()
    parser.add_argument(
        "--target", type=Path, help="Target directory or file", required=True
    )

    args = parser.parse_args()

    result = call_target(args)
    handle_result(result, args.target)
