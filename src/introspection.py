from argparse import ArgumentParser
from inspect import getfullargspec
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

import pvinspect as pv  # type: ignore
from docstring_parser import parse  # type: ignore
from docstring_parser.common import DocstringParam  # type: ignore


def parse_method_description(func: Callable) -> Tuple[Optional[str], Optional[str]]:
    if func.__doc__:
        parsed_doc = parse(func.__doc__)
        return parsed_doc.short_description, parsed_doc.long_description

    return None, None


def add_command_arguments(func: Callable, subparser: ArgumentParser) -> None:
    doc = func.__doc__

    if doc:
        parsed_doc = parse(doc)

        # parse parameter descriptions and types
        params_and_types: Dict[str, DocstringParam] = dict()
        for p in parsed_doc.params:
            if p.type_name:
                params_and_types[p.arg_name] = p

        # parse params and defaults using inspect
        args, _, _, defaults, _, _, _ = getfullargspec(func)

        # convert to list of the same length as args
        defaults_list = [None] * len(args)
        if defaults:
            defaults_list = [None] * (len(args) - len(defaults)) + list(defaults)

        # handler functions that are called per argument before fn is finally called
        handlers = dict()

        for arg, default in zip(args, defaults_list):

            p = params_and_types[arg]
            t = p.type_name.split(".")[-1]

            # single image
            if t == "Image":
                subparser.add_argument(
                    "--{}".format(p.arg_name),
                    type=Path,
                    required=default is None,
                    help=p.description,
                )
                handlers[arg] = pv.data.io.read_image

            # image sequence
            if t == "ImageSequence":
                subparser.add_argument(
                    "--{}".format(p.arg_name),
                    nargs="+",
                    type=Path,
                    required=default is None,
                    help=p.description,
                )
                handlers[arg] = lambda x: pv.data.ImageSequence(
                    [pv.data.io.read_image(y) for y in x]
                )

            if t == "float":
                subparser.add_argument(
                    "--{}".format(p.arg_name),
                    type=float,
                    required=default is None,
                    default=default,
                    help=p.description,
                )

            if t == "int":
                subparser.add_argument(
                    "--{}".format(p.arg_name),
                    type=int,
                    required=default is None,
                    default=default,
                    help=p.description,
                )

            if t == "str":
                subparser.add_argument(
                    "--{}".format(p.arg_name),
                    type=str,
                    required=default is None,
                    default=default,
                    help=p.description,
                )

            if t == "bool" and (default==False or default==None):
                subparser.add_argument(
                    "--{}".format(p.arg_name),
                    required=default is None,
                    help=p.description,
                    action="store_true",
                )
            elif t == "bool" and default==True:
                argname = p.arg_name
                if argname.startswith("enable"):
                    argname = argname.replace("enable", "disable")
                else:
                    argname = "disable_"+argname
                description = p.description.replace("enable", "disable")
                description = p.description.replace("Enable", "Disable")
                subparser.add_argument(
                    "--{}".format(argname),
                    required=False,
                    default=True,
                    help=description,
                    action="store_false",
                    dest=p.arg_name
                )

        # store handles and fn with the arguments
        subparser.set_defaults(_handlers=handlers, _func=func)

