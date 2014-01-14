# -*- coding: utf-8 -*-

import os
import sys

_CUR_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(_CUR_DIR))

from collections import namedtuple

import etch

PFAT = namedtuple("PositionalFormatArgTest", "fstr arg_vals res")


_PFATS = [PFAT('{} {} {}', ('hi', 'hello', 'bye'), "hi hello bye"),
          PFAT('{:d} {}', (1, 2), "1 2"),
          PFAT('{!s} {!r}', ('str', 'repr'), "str 'repr'"),
          PFAT('{{joek}} ({} {})', ('so', 'funny'), "{joek} (so funny)"),
          PFAT('{[hi]}, {.__name__!r}',
               ({'hi': 'hi'}, PFAT),
               "hi, %r" % PFAT.__name__)]


def test_pos_infer():
    for i, (tmpl, args, res) in enumerate(_PFATS):
        converted = etch.infer_positional_format_args(tmpl)
        assert converted.format(*args) == res


_TEST_TMPLS = ["example 1: {hello}",
               "example 2: {hello:*10}",
               "example 3: {hello:*{width}}",
               "example 4: {hello!r:{fchar}{width}}, {width}, yes",
               "example 5: {0}, {1:d}, {2:f}, {1}",
               "example 6: {}, {}, {}, {1}"]


def test_get_fstr_args():
    results = []
    for t in _TEST_TMPLS:
        inferred_t = etch.infer_positional_format_args(t)
        res = etch.get_format_args(inferred_t)
        #print res
        results.append(res)
    return results


def test_split_fstr():
    results = []
    for t in _TEST_TMPLS:
        res = etch.split_format_str(t)
        #print res
        results.append(res)
    return results


def test_tokenize_format_str():
    results = []
    for t in _TEST_TMPLS:
        res = etch.tokenize_format_str(t)
        print ''.join([str(r) for r in res])
        results.append(res)
    return results


if __name__ == '__main__':
    test_tokenize_format_str()
    test_split_fstr()
    test_pos_infer()
    test_get_fstr_args()
