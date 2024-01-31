### SPDX-License-Identifier: GPL-2.0-or-later

"""Log message sources."""

import json
from decimal import Decimal


def logged(file, parser):
    """Generator yielding (id_, data) for lines in `file` parsed by `parser`.

    `id_` is the value of the corresponding parser attribute;
    `data` is the canonical data produced by `parser` for a line.

    `file` is closed just before returning.
    """
    while True:
        line = file.readline()
        if line == '':
            file.close()
            return
        data = parser.parse_line(line.rstrip())
        if data is not None:
            yield (parser.id_, data)


def muxed(file, parsers):
    """Generator yielding (id_, data) for multiplexed content in `file`.

    Each line in `file` must be a JSON-encoded object with pairs at 'id' and
    'data'. If there is no parser for the value at 'id' in `parsers`, then the
    line is discarded: otherwise a pair is generated.

    `id_` is the value at 'id';
    `data`  the values within data must be the equivalent to  canonical data
    produced by the parser at `id_` in `parsers` for the value at 'data'.
    They can be in the form of a JSON array or a JSON object.
    If the data is a JSON array then the ordering must match the parser output.
    If the data is a JSON object then the names must match the parser output.


    `file` is closed just before returning.
    """
    while True:
        line = file.readline()
        if line == '':
            file.close()
            return
        obj = json.loads(line.rstrip(), parse_float=Decimal)
        id_ = obj['id']
        try:
            parser = parsers[id_]
        except KeyError:
            pass
        else:
            if isinstance(obj['data'], dict):
                data = tuple(obj['data'][name] for name in parser.elems)
            else:
                data = obj['data']
            parsed = parser.make_parsed(data)
            yield (id_, parsed)
