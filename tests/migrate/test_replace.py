# coding=utf8
from __future__ import unicode_literals

import unittest

import fluent.syntax.ast as FTL
try:
    from compare_locales.parser import PropertiesParser
except ImportError:
    PropertiesParser = None

from fluent.migrate.util import parse, ftl_message_to_json
from fluent.migrate.helpers import EXTERNAL_ARGUMENT
from fluent.migrate.transforms import evaluate, REPLACE


class MockContext(unittest.TestCase):
    def get_source(self, path, key):
        return self.strings.get(key, None).val


@unittest.skipUnless(PropertiesParser, 'compare-locales required')
class TestReplaceExplicit(MockContext):
    def setUp(self):
        self.strings = parse(PropertiesParser, '''
            hello = Hello, #1!
            welcome = Welcome, #1, to #2!
            first = #1 Bar
            last = Foo #1
        ''')

    def test_replace_one(self):
        msg = FTL.Message(
            FTL.Identifier(u'hello'),
            value=REPLACE(
                self.strings,
                'hello',
                {
                    '#1': EXTERNAL_ARGUMENT('username')
                }
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                hello = Hello, { $username }!
            ''')
        )

    def test_replace_two(self):
        msg = FTL.Message(
            FTL.Identifier(u'welcome'),
            value=REPLACE(
                self.strings,
                'welcome',
                {
                    '#1': EXTERNAL_ARGUMENT('username'),
                    '#2': EXTERNAL_ARGUMENT('appname')
                }
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                welcome = Welcome, { $username }, to { $appname }!
            ''')
        )

    def test_replace_too_many(self):
        msg = FTL.Message(
            FTL.Identifier(u'welcome'),
            value=REPLACE(
                self.strings,
                'welcome',
                {
                    '#1': EXTERNAL_ARGUMENT('username'),
                    '#2': EXTERNAL_ARGUMENT('appname'),
                    '#3': EXTERNAL_ARGUMENT('extraname')
                }
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                welcome = Welcome, { $username }, to { $appname }!
            ''')
        )

    def test_replace_too_few(self):
        msg = FTL.Message(
            FTL.Identifier(u'welcome'),
            value=REPLACE(
                self.strings,
                'welcome',
                {
                    '#1': EXTERNAL_ARGUMENT('username')
                }
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                welcome = Welcome, { $username }, to #2!
            ''')
        )

    def test_replace_first(self):
        msg = FTL.Message(
            FTL.Identifier(u'first'),
            value=REPLACE(
                self.strings,
                'first',
                {
                    '#1': EXTERNAL_ARGUMENT('foo')
                }
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                first = { $foo } Bar
            ''')
        )

    def test_replace_last(self):
        msg = FTL.Message(
            FTL.Identifier(u'last'),
            value=REPLACE(
                self.strings,
                'last',
                {
                    '#1': EXTERNAL_ARGUMENT('bar')
                }
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                last = Foo { $bar }
            ''')
        )


@unittest.skipUnless(PropertiesParser, 'compare-locales required')
class TestReplaceStringBundle(MockContext):
    def setUp(self):
        self.strings = parse(PropertiesParser, '''
            implicit = %S %S
            explicit = %2$S %1$S
            zero-width-implicit = %S%0.S
            zero-width-explicit = %2$S%1$0.S
        ''')

    def test_replace_implicit(self):
        msg = FTL.Message(
            FTL.Identifier('implicit'),
            value=REPLACE(
                self.strings,
                'implicit',
                (
                    EXTERNAL_ARGUMENT('one'),
                    EXTERNAL_ARGUMENT('two')
                )
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                implicit = { $one } { $two }
            ''')
        )

    def test_replace_implicit_too_many(self):
        msg = FTL.Message(
            FTL.Identifier('implicit'),
            value=REPLACE(
                self.strings,
                'implicit',
                (
                    EXTERNAL_ARGUMENT('one'),
                    EXTERNAL_ARGUMENT('two'),
                    EXTERNAL_ARGUMENT('three'),
                )
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                implicit = { $one } { $two }
            ''')
        )

    def test_replace_implicit_too_few(self):
        msg = FTL.Message(
            FTL.Identifier('implicit'),
            value=REPLACE(
                self.strings,
                'implicit',
                (
                    EXTERNAL_ARGUMENT('one'),
                )
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                implicit = { $one } %S
            ''')
        )

    def test_replace_explicit(self):
        msg = FTL.Message(
            FTL.Identifier('explicit'),
            value=REPLACE(
                self.strings,
                'explicit',
                (
                    EXTERNAL_ARGUMENT('one'),
                    EXTERNAL_ARGUMENT('two')
                )
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                explicit = { $two } { $one }
            ''')
        )

    def test_replace_explicit_too_many(self):
        msg = FTL.Message(
            FTL.Identifier('explicit'),
            value=REPLACE(
                self.strings,
                'explicit',
                (
                    EXTERNAL_ARGUMENT('one'),
                    EXTERNAL_ARGUMENT('two'),
                    EXTERNAL_ARGUMENT('three'),
                )
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                explicit = { $two } { $one }
            ''')
        )

    def test_replace_explicit_too_few(self):
        msg = FTL.Message(
            FTL.Identifier('explicit'),
            value=REPLACE(
                self.strings,
                'explicit',
                (
                    EXTERNAL_ARGUMENT('one'),
                )
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                explicit = %2$S { $one }
            ''')
        )

    def test_replace_zero_width_implicit(self):
        msg = FTL.Message(
            FTL.Identifier('zero-width-implicit'),
            value=REPLACE(
                self.strings,
                'zero-width-implicit',
                (
                    EXTERNAL_ARGUMENT('one'),
                    EXTERNAL_ARGUMENT('two')
                )
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                zero-width-implicit = { $one }
            ''')
        )

    def test_replace_zero_width_explicit(self):
        msg = FTL.Message(
            FTL.Identifier('zero-width-explicit'),
            value=REPLACE(
                self.strings,
                'zero-width-explicit',
                (
                    EXTERNAL_ARGUMENT('one'),
                    EXTERNAL_ARGUMENT('two')
                )
            )
        )

        self.assertEqual(
            evaluate(self, msg).to_json(),
            ftl_message_to_json('''
                zero-width-explicit = { $two }
            ''')
        )


if __name__ == '__main__':
    unittest.main()
