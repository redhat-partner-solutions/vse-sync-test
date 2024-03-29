### SPDX-License-Identifier: GPL-2.0-or-later

"""Sequence log messages from multiple sources."""

from argparse import ArgumentParser
import sys
from sys import stdin

from collections import namedtuple
import yaml

from .common import print_loj

from .parsers import PARSERS
from .source import (
    logged,
    muxed,
)


def build_emit(available, include=(), exclude=()):
    """Return a frozenset of ids to emit.

    If `include` is empty, then return ids in `available` but not in `exclude`.
    Otherwise, return ids in `available` and `include` but not in `exclude`.
    """
    ava = frozenset(available)
    inc = frozenset(include)
    exc = frozenset(exclude)
    return ava.intersection(inc or ava).difference(exc)


def build_sources(parsers, filename, encoding='utf-8'):
    """Generator yielding (id_, data) generators for sources in `filename`"""
    parsers = {id_: cls() for (id_, cls) in parsers.items()}
    with open(filename, encoding=encoding) as fid:
        for obj in yaml.safe_load_all(fid.read()):
            source = obj['source']
            contains = obj['contains']
            file = stdin if source == '-' else open(source, encoding=encoding)
            if contains == 'muxed':
                yield muxed(file, parsers)
            else:
                yield logged(file, parsers[contains])


# tuple of the most recent values generated by source
# timestamp must be first and numeric
Head = namedtuple('Head', ('timestamp', 'id_', 'data', 'source'))


def build_head(source):
    """Return a :class:`Head` value or None from the next item in `source`."""
    try:
        (id_, data) = next(source)
        return Head(data.timestamp, id_, data, source)
    except StopIteration:
        return None


def build_heads(sources):
    """Return a list of :class:`Head` values from the first items in `sources`.

    The returned list is sorted by timestamp in ascending order.
    """
    heads = []
    for source in sources:
        head = build_head(source)
        if head:
            heads.append(head)
    return sorted(heads)


def insert_head(heads, head):
    """Return `heads` with `head` inserted in ascending timestamp order.

    If `head` is None then do not insert `head`.
    """
    if head is None:
        return heads
    idx = 0
    while idx < len(heads):
        if head.timestamp < heads[idx].timestamp:
            break
        idx += 1
    heads.insert(idx, head)
    return heads


def main():
    """Sequence log messages from multiple sources to stdout.

    Log messages are read from files specified in the YAML file supplied in
    command line argument `sources`. This YAML file may contain multiple
    documents, with each document containing a single object with 'source' and
    'contains' pairs. 'source' specifies a file to read from or '-' to read from
    stdin; 'contains' specifies the content in the file, either the id of a
    supported parser (as listed in command line help for options `--include`
    and `--exclude`) or 'muxed' for multiplexed content.

    Each line in multiplexed content must be a JSON-encoded object with 'id' and
    'data' pairs. 'id' must be the id of a supported parser; 'data' a value
    conforming to the canonical form produced by that parser.

    The output written to stdout is multiplexed content, with lines sequenced as
    follows. An initial set of candidate messages to write is constructed by
    parsing the first log message from each source. The message with the lowest
    timestamp in this set is written to stdout before being replaced by the next
    log message from its source. This process is repeated until all sources are
    empty. (For the avoidance of doubt, log messages within a single source are
    not sequenced by this tool: they are processed in file order.)
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        '--include', choices=PARSERS, nargs='*', default=(),
        help='restrict output messages to these parsers',
    )
    aparser.add_argument(
        '--exclude', choices=PARSERS, nargs='*', default=(),
        help='never output messages for these parsers (overriding)',
    )
    aparser.add_argument(
        'sources',
        help='YAML file specifying sources of log messages',
    )
    args = aparser.parse_args()
    emit = build_emit(PARSERS, args.include, args.exclude)
    sources = tuple(build_sources(PARSERS, args.sources))
    heads = build_heads(sources)
    while heads:
        first = heads.pop(0)
        if first.id_ in emit:
            obj = {'id': first.id_, 'data': first.data}
            # Python exits with error code 1 on EPIPE
            if not print_loj(obj):
                sys.exit(1)
        heads = insert_head(heads, build_head(first.source))


if __name__ == '__main__':
    main()
