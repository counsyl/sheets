import datetime
import decimal
from itertools import izip
import unittest

import sheets


class ColumnTests(unittest.TestCase):
    invalid_values = []

    def setUp(self):
        self.column = sheets.Column()
        self.string_values = ['value']
        self.python_values = ['value']

    def test_validation(self):
        for pyval in self.python_values:
            try:
                self.column.validate(pyval)
            except ValueError as e:
                self.fail(unicode(e))

    def test_python_conversion(self):
        for sval, pval in izip(self.string_values, self.python_values):
            python_value = self.column.to_python(sval)
            self.assertEqual(python_value, pval)

    def test_string_conversion(self):
        for sval, pval in izip(self.string_values, self.python_values):
            string_value = str(self.column.to_string(pval))
            self.assertEqual(string_value, sval)

    def test_invalid_value(self):
        for value in self.invalid_values:
            try:
                value = self.column.to_python(value)
            except ValueError:
                # If it's caught here, there's no need to test anything else
                return
            self.assertRaises(ValueError, self.column.validate, value)


class StringColumnTests(ColumnTests):
    def setUp(self):
        self.column = sheets.StringColumn()
        self.string_values = ['value']
        self.python_values = ['value']


class UnicodeColumnTests_UTF8(ColumnTests):
    def setUp(self):
        self.column = sheets.UnicodeColumn(encoding='utf-8')
        self.string_values = ['Spin\xcc\x88al Tap']
        self.python_values = [u'Spin\u0308al Tap']


class UnicodeColumnTests_UTF16(ColumnTests):
    def setUp(self):
        self.column = sheets.UnicodeColumn(encoding='utf-16')
        self.string_values = [('\xff\xfeS\x00p\x00i\x00n\x00\x08\x03'
                               'a\x00l\x00 \x00T\x00a\x00p\x00')]
        self.python_values = [u'Spin\u0308al Tap']


class IntegerColumnTests(ColumnTests):
    def setUp(self):
        self.column = sheets.IntegerColumn()
        self.string_values = ['1']
        self.python_values = [1]
        self.invalid_values = ['invalid']


class FloatColumnTests(ColumnTests):
    def setUp(self):
        self.column = sheets.FloatColumn()
        self.string_values = ['1.1']
        self.python_values = [1.1]
        self.invalid_values = ['invalid']


class FloatWithCommaSeparatorsColumnTests(ColumnTests):
    def setUp(self):
        self.column = sheets.FloatWithCommaSeparatorsColumn()
        self.string_values = ['1,024.5']
        self.python_values = [1024.5]
        self.invalid_values = ['in,valid', '1.2,3.4,5.6']


class BooleanColumnTests(ColumnTests):
    def setUp(self):
        self.column = sheets.BooleanColumn()
        self.string_values = ['true', 'false']
        self.python_values = [True, False]
        self.invalid_values = ['yes', 'True']


class MappedBooleanColumnTests(ColumnTests):
    def setUp(self):
        self.column = sheets.BooleanColumn(bool_map={'yes': True, 'no': False})
        self.string_values = ['yes', 'no']
        self.python_values = [True, False]
        self.invalid_values = ['true', 'false']


class DecimalColumnTests(ColumnTests):
    def setUp(self):
        self.column = sheets.DecimalColumn()
        self.string_values = ['1.1']
        self.python_values = [decimal.Decimal('1.1')]
        self.invalid_values = ['invalid']


class DateColumnTests(ColumnTests):
    def setUp(self):
        self.column = sheets.DateColumn()
        self.string_values = ['2010-03-31']
        self.python_values = [datetime.date(2010, 3, 31)]
        self.invalid_values = ['invalid', '03-31-2010']


class FormattedDateColumnTests(ColumnTests):
    def setUp(self):
        self.column = sheets.DateColumn(format='%m/%d/%Y')
        self.string_values = ['03/31/2010']
        self.python_values = [datetime.date(2010, 3, 31)]
        self.invalid_values = ['invalid', '03-31-2010']


class DateTimeColumnTests(ColumnTests):
    def setUp(self):
        self.column = sheets.DateTimeColumn()
        self.string_values = ['2010-03-31']
        self.python_values = [datetime.datetime(2010, 3, 31)]
        self.invalid_values = ['invalid', '03-31-2010']


class FormattedDateTimeColumnTests(ColumnTests):
    def setUp(self):
        self.column = sheets.DateTimeColumn(format='%m/%d/%Y %H:%M:%S')
        self.string_values = ['03/31/2010 11:43:12']
        self.python_values = [datetime.datetime(2010, 3, 31, 11, 43, 12)]
        self.invalid_values = ['invalid', '03/31/2010']
