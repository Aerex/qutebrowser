# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2014-2015 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for qutebrowser.misc.split."""
import collections

import pytest

from qutebrowser.misc import split


# Most tests copied from Python's shlex.
# The original test data set was from shellwords, by Hartmut Goebel.

# Format: input/split|output|without|keep/split|output|with|keep/

test_data_str = r"""
one two/one|two/one| two/
one "two three" four/one|two three|four/one| "two three"| four/
one 'two three' four/one|two three|four/one| 'two three'| four/
one "two\" three" four/one|two" three|four/one| "two\" three"| four/
one 'two'\'' three' four/one|two' three|four/one| 'two'\'' three'| four/
one "two three/one|two three/one| "two three/
one 'two three/one|two three/one| 'two three/
one\/one\/one\/
one "two\/one|two\/one| "two\/
one /one/one| /
open -t i/open|-t|i/open| -t| i/
foo bar/foo|bar/foo| bar/
 foo bar/foo|bar/ foo| bar/
 foo bar /foo|bar/ foo| bar| /
foo   bar    bla     fasel/foo|bar|bla|fasel/foo|   bar|    bla|     fasel/
x y  z              xxxx/x|y|z|xxxx/x| y|  z|              xxxx/
\x bar/x|bar/\x| bar/
\ x bar/ x|bar/\ x| bar/
\ bar/ bar/\ bar/
foo \x bar/foo|x|bar/foo| \x| bar/
foo \ x bar/foo| x|bar/foo| \ x| bar/
foo \ bar/foo| bar/foo| \ bar/
foo "bar" bla/foo|bar|bla/foo| "bar"| bla/
"foo" "bar" "bla"/foo|bar|bla/"foo"| "bar"| "bla"/
"foo" bar "bla"/foo|bar|bla/"foo"| bar| "bla"/
"foo" bar bla/foo|bar|bla/"foo"| bar| bla/
foo 'bar' bla/foo|bar|bla/foo| 'bar'| bla/
'foo' 'bar' 'bla'/foo|bar|bla/'foo'| 'bar'| 'bla'/
'foo' bar 'bla'/foo|bar|bla/'foo'| bar| 'bla'/
'foo' bar bla/foo|bar|bla/'foo'| bar| bla/
blurb foo"bar"bar"fasel" baz/blurb|foobarbarfasel|baz/blurb| foo"bar"bar"fasel"| baz/
blurb foo'bar'bar'fasel' baz/blurb|foobarbarfasel|baz/blurb| foo'bar'bar'fasel'| baz/
""//""/
''//''/
foo "" bar/foo||bar/foo| ""| bar/
foo '' bar/foo||bar/foo| ''| bar/
foo "" "" "" bar/foo||||bar/foo| ""| ""| ""| bar/
foo '' '' '' bar/foo||||bar/foo| ''| ''| ''| bar/
\"/"/\"/
"\""/"/"\""/
"foo\ bar"/foo\ bar/"foo\ bar"/
"foo\\ bar"/foo\ bar/"foo\\ bar"/
"foo\\ bar\""/foo\ bar"/"foo\\ bar\""/
"foo\\" bar\"/foo\|bar"/"foo\\"| bar\"/
"foo\\ bar\" dfadf"/foo\ bar" dfadf/"foo\\ bar\" dfadf"/
"foo\\\ bar\" dfadf"/foo\\ bar" dfadf/"foo\\\ bar\" dfadf"/
"foo\\\x bar\" dfadf"/foo\\x bar" dfadf/"foo\\\x bar\" dfadf"/
"foo\x bar\" dfadf"/foo\x bar" dfadf/"foo\x bar\" dfadf"/
\'/'/\'/
'foo\ bar'/foo\ bar/'foo\ bar'/
'foo\\ bar'/foo\\ bar/'foo\\ bar'/
"foo\\\x bar\" df'a\ 'df"/foo\\x bar" df'a\ 'df/"foo\\\x bar\" df'a\ 'df"/
\"foo/"foo/\"foo/
\"foo\x/"foox/\"foo\x/
"foo\x"/foo\x/"foo\x"/
"foo\ "/foo\ /"foo\ "/
foo\ xx/foo xx/foo\ xx/
foo\ x\x/foo xx/foo\ x\x/
foo\ x\x\"/foo xx"/foo\ x\x\"/
"foo\ x\x"/foo\ x\x/"foo\ x\x"/
"foo\ x\x\\"/foo\ x\x\/"foo\ x\x\\"/
"foo\ x\x\\""foobar"/foo\ x\x\foobar/"foo\ x\x\\""foobar"/
"foo\ x\x\\"\'"foobar"/foo\ x\x\'foobar/"foo\ x\x\\"\'"foobar"/
"foo\ x\x\\"\'"fo'obar"/foo\ x\x\'fo'obar/"foo\ x\x\\"\'"fo'obar"/
"foo\ x\x\\"\'"fo'obar" 'don'\''t'/foo\ x\x\'fo'obar|don't/"foo\ x\x\\"\'"fo'obar"| 'don'\''t'/
"foo\ x\x\\"\'"fo'obar" 'don'\''t' \\/foo\ x\x\'fo'obar|don't|\/"foo\ x\x\\"\'"fo'obar"| 'don'\''t'| \\/
'foo\ bar'/foo\ bar/'foo\ bar'/
'foo\\ bar'/foo\\ bar/'foo\\ bar'/
foo\ bar/foo bar/foo\ bar/
:-) ;-)/:-)|;-)/:-)| ;-)/
áéíóú/áéíóú/áéíóú/
"""


def _parse_split_test_data_str():
    """
    Parse the test data set into a namedtuple to use in tests.

    Returns:
        A list of namedtuples with str attributes: input, keep, no_keep
    """
    tuple_class = collections.namedtuple('TestCase', 'input, keep, no_keep')

    for line in test_data_str.splitlines():
        if not line:
            continue
        data = line.split('/')
        item = tuple_class(input=data[0], keep=data[1].split('|'),
                           no_keep=data[2].split('|'))
        yield item
    yield tuple_class(input='', keep=[], no_keep=[])


class TestSplit:

    """Test split."""

    @pytest.fixture(params=_parse_split_test_data_str())
    def split_test_case(self, request):
        """Fixture to automatically parametrize all depending tests.

        It will use the test data from test_data_str, parsed using
        _parse_split_test_data_str().
        """
        return request.param

    def test_split(self, split_test_case):
        """Test splitting."""
        items = split.split(split_test_case.input)
        assert items == split_test_case.keep

    def test_split_keep_original(self, split_test_case):
        """Test if splitting with keep=True yields the original string."""
        items = split.split(split_test_case.input, keep=True)
        assert ''.join(items) == split_test_case.input

    def test_split_keep(self, split_test_case):
        """Test splitting with keep=True."""
        items = split.split(split_test_case.input, keep=True)
        assert items == split_test_case.no_keep


class TestSimpleSplit:

    """Test simple_split."""

    TESTS = {
        ' foo bar': [' foo', ' bar'],
        'foobar': ['foobar'],
        '   foo  bar baz  ': ['   foo', '  bar', ' baz', '  '],
        'f\ti\ts\th': ['f', '\ti', '\ts', '\th'],
        'foo\nbar': ['foo', '\nbar'],
    }

    @pytest.mark.parametrize('test', TESTS)
    def test_str_split(self, test):
        """Test if the behavior matches str.split."""
        assert split.simple_split(test) == test.rstrip().split()

    @pytest.mark.parametrize('s, maxsplit',
                             [("foo bar baz", 1), ("  foo bar baz  ", 0)])
    def test_str_split_maxsplit(self, s, maxsplit):
        """Test if the behavior matches str.split with given maxsplit."""
        actual = split.simple_split(s, maxsplit=maxsplit)
        expected = s.rstrip().split(maxsplit=maxsplit)
        assert actual == expected

    @pytest.mark.parametrize('test, expected', TESTS.items())
    def test_split_keep(self, test, expected):
        """Test splitting with keep=True."""
        assert split.simple_split(test, keep=True) == expected
