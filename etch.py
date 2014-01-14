# -*- coding: utf-8 -*-
"""
Etch
~~~~

Etch aims to be a minimalist string templating framework, ostensibly
built on Python's advanced string formatting functionality, as described in
PEP 3101 and here: http://docs.python.org/2/library/string.html#format-specification-mini-language

Python's str.format()-style formatting has the following deal-breakers:

- raises KeyError when a key is not provided (e.g., '{x}'.format() )
- no fallback behavior when a value fails to format/render
- inconsistent feature support (2.6 doesn't support '{}'.format('hi'))

There are pros and cons to doing it this way.

Pros:

- Small/single-file library
- Uses the built-in Python format string parser (which is C, ostensibly fast)
- Familiar syntax and featureset

Cons:

- Actual rendering is still Python, not the fastest, but fast enough
- Python's new-style string formatting is idiosyncratic at best

  - Lackluster error reporting
  - Not very extensible

- Many features are still fairly obscure
- Few escaping functions suitable to certain applications (XML/HTML/JS escapes)
- No loops or conditionals
- Format fields give 'conversion' functions (i.e., repr() and str()), but no
  mechanism for post-conversion processing (might have to be built-in to the
  processor)
"""

import re
from string import Formatter

__version__ = '0.0.1'
__author__ = 'Mahmoud Hashemi'
__contact__ = 'mahmoudrhashemi@gmail.com'
__url__ = 'https://github.com/mahmoud/etch'
__license__ = 'BSD'


_pos_farg_re = re.compile('({{)|'         # escaped open-brace
                          '(}})|'         # escaped close-brace
                          '({[:!.\[}])')  # anon positional format arg


def construct_format_field_str(fname, fspec, conv):
    if fname is None:
        return ''
    ret = '{' + fname
    if conv:
        ret += '!' + conv
    if fspec:
        ret += ':' + fspec
    ret += '}'
    return ret


def split_format_str(fstr):
    ret = []
    for lit, fname, fspec, conv in fstr._formatter_parser():
        if fname is None:
            ret.append((lit, None))
            continue
        field_str = construct_format_field_str(fname, fspec, conv)
        ret.append((lit, field_str))
    return ret


def infer_positional_format_args(fstr):
    # TODO: memoize
    ret, max_anon = '', 0
    # look for {: or {! or {. or {[ or {}
    start, end, prev_end = 0, 0, 0
    for match in _pos_farg_re.finditer(fstr):
        start, end, group = match.start(), match.end(), match.group()
        if prev_end < start:
            ret += fstr[prev_end:start]
        prev_end = end
        if group == '{{' or group == '}}':
            ret += group
            continue
        ret += '{%s%s' % (max_anon, group[1:])
        max_anon += 1
    ret += fstr[prev_end:]
    return ret


_INTCHARS = 'bcdoxXn'
_FLOATCHARS = 'eEfFgGn%'
_TYPE_MAP = dict([(x, int) for x in _INTCHARS] +
                 [(x, float) for x in _FLOATCHARS])
_TYPE_MAP['s'] = str


def get_format_args(fstr):
    # TODO: memoize
    formatter = Formatter()
    fargs, fkwargs, _dedup = [], [], set()

    def _add_arg(argname, type_char='s'):
        if argname not in _dedup:
            _dedup.add(argname)
            argtype = _TYPE_MAP.get(type_char, str)  # TODO: unicode
            try:
                fargs.append((int(argname), argtype))
            except ValueError:
                fkwargs.append((argname, argtype))

    for lit, fname, fspec, conv in formatter.parse(fstr):
        if fname is not None:
            type_char = fspec[-1:]
            fname_list = re.split('[.[]', fname)
            if len(fname_list) > 1:
                raise ValueError('encountered compound format arg: %r' % fname)
            try:
                base_fname = fname_list[0]
                assert base_fname
            except (IndexError, AssertionError):
                raise ValueError('encountered anonymous positional argument')
            _add_arg(fname, type_char)
            for sublit, subfname, _, _ in formatter.parse(fspec):
                # TODO: positional and anon args not allowed here.
                if subfname is not None:
                    _add_arg(subfname)
    return fargs, fkwargs


def tokenize_format_str(fstr, resolve_pos=True):
    ret = []
    if resolve_pos:
        fstr = infer_positional_format_args(fstr)
    formatter = Formatter()
    for lit, fname, fspec, conv in formatter.parse(fstr):
        if lit:
            ret.append(lit)
        if fname is None:
            continue
        ret.append(BaseFormatField(fname, fspec, conv))
    return ret


class BaseFormatField(object):
    def __init__(self, fname, fspec='', conv=None):
        self.set_fname(fname)
        self.set_fspec(fspec)
        self.set_conv(conv)

    def set_fname(self, fname):
        path_list = re.split('[.[]', fname)  # TODO

        self.base_name = path_list[0]
        self.fname = fname
        self.subpath = path_list[1:]
        self.is_positional = not self.base_name or self.base_name.isdigit()

    def set_fspec(self, fspec):
        fspec = fspec or ''
        subfields = []
        for sublit, subfname, _, _ in fspec._formatter_parser():
            if subfname is not None:
                subfields.append(subfname)
        self.subfields = subfields
        self.fspec = fspec
        self.type_char = fspec[-1:]
        self.type_func = _TYPE_MAP.get(self.type_char, str)

    def set_conv(self, conv):
        "!s and !r, etc."
        # TODO
        self.conv = conv
        self.conv_func = None  # TODO

    @property
    def fstr(self):
        return construct_format_field_str(self.fname, self.fspec, self.conv)

    def __repr__(self):
        cn = self.__class__.__name__
        args = [self.fname]
        if self.conv is not None:
            args.extend([self.fspec, self.conv])
        elif self.fspec != '':
            args.append(self.fspec)
        args_repr = ', '.join([repr(a) for a in args])
        return '%s(%s)' % (cn, args_repr)

    def __str__(self):
        return self.fstr


class Etcher(object):
    def __init__(self, tmpl_str, quoter=None, defaulter=None):
        self.defaulter = defaulter or (lambda t: str(t))
        if not callable(self.defaulter):
            raise TypeError()
        self.quoter = quoter or self._default_quoter
        if not callable(self.quoter):
            raise TypeError()
        # self.getters = getters  # dict, handled at class level now

        self.raw_tmpl_str = tmpl_str
        self.tokens = tokenize_format_str(tmpl_str)
        self.default_map = {}
        self.quote_map = {}
        for token in self.tokens:
            try:
                fspec = token.fspec
                self.default_map[token] = self.defaulter(token)
                self.quote_map[token] = self.quoter(token)
                if not fspec:
                    token.set_fspec('s')
            except (KeyError, AttributeError):
                # not a field or not a builtin field
                pass
        return

    def format(self, *args, **kwargs):
        ret = ''
        for t in self.tokens:
            try:
                name = t.base_name
            except AttributeError:
                ret += t
                continue
            try:
                if t.is_positional:
                    seg = t.fstr.format(*args)
                else:
                    seg = t.fstr.format(**{name: kwargs[name]})
                #if self.quote_map[t]:
                #    seg = escape_str(seg)
                ret += seg
            except:
                ret += self.default_map[t]
        return ret

    __call__ = format


if __name__ == '__main__':
    x = tokenize_format_str('hi {thing!z}')
    print x
    import pdb;pdb.set_trace()
