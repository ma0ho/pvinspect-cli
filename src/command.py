from argparse import ArgumentDefaultsHelpFormatter, Namespace
from pathlib import Path
from typing import Any, Callable, Dict

import pvinspect as pv  # type: ignore

from .introspection import add_command_arguments, parse_method_description


def call_target(args: Namespace) -> Any:

    # wrapper, which takes the specified _func and _handlers and
    # calls _handlers on the arguments and then calls _func
    def wrap(_func: Callable, _handlers: Dict[str, Callable], target: Path, **kwargs):
        # call specified handlers
        for k, f in _handlers.items():
            kwargs[k] = f(kwargs[k])

        # call actual function
        return _func(**kwargs)

    return wrap(**vars(args))


def handle_result(result: Any, target: Path):
    if isinstance(result, pv.data.Image):
        pv.data.io.save_image(target, result)
    elif isinstance(result, pv.data.ImageSequence):
        pv.data.io.save_images(target, result)
    else:
        raise NotImplementedError()


def setup_command(fn: Callable, name: str, subparsers):
    sd, ld = parse_method_description(fn)

    desc = ""
    if sd is not None and ld is None:
        desc = sd
    if sd is not None and ld is not None:
        desc = sd + "\n" + ld

    p = subparsers.add_parser(
        name, formatter_class=ArgumentDefaultsHelpFormatter, description=desc
    )
    add_command_arguments(fn, p)
