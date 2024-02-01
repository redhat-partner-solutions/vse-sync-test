### SPDX-License-Identifier: GPL-2.0-or-later

"""Validate XML against a XSD schema"""

import sys
from argparse import ArgumentParser

from xml.etree import ElementTree

import xmlschema
from xmlschema.validators.exceptions import XMLSchemaValidationError


def validate(schema, filename):
    """Validate XML in `filename` against XSD `schema`.

    Return True on validation success, or a string reason on validation failure.
    """
    try:
        xmlschema.validate(filename, schema)
        return True
    except XMLSchemaValidationError as exc:
        return str(exc)


def prettify(filename):
    """Return prettified XML from `filename`."""
    et_ = ElementTree.parse(filename)
    ElementTree.indent(et_)
    return ElementTree.tostring(et_.getroot(), encoding="unicode")


def source(filename, encoding="utf-8"):
    """Return source text from `filename`."""
    with open(filename, encoding=encoding) as fid:
        return fid.read()


def main():
    """Validate XML against a XSD schema, printing valid XML to stdout"""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        "--verbose",
        action="store_true",
        help="print validation failure reason on error",
    )
    aparser.add_argument(
        "--prettify",
        action="store_true",
        help="pretty print XML output",
    )
    aparser.add_argument("schema", help="XSD schema file")
    aparser.add_argument("filename", help="XML data file")
    args = aparser.parse_args()
    reason = validate(args.schema, args.filename)
    if reason is not True:
        sys.exit(reason if args.verbose else 1)
    elif args.prettify:
        print(prettify(args.filename))
    else:
        print(source(args.filename), end="")


if __name__ == "__main__":
    main()
