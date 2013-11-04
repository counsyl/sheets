import datetime
import decimal
import functools

from itertools import count


class Column(object):
    """An individual column within a CSV file.

    This serves as a base for attributes and methods that are common to all
    types of columns. Subclasses of Column will define behavior for more
    specific data types.
    """

    _count = count()  # global counter to maintain attr order this can be
                      # removed in python 3.0 with metaclass.__prepare__.

    def __init__(self, title=None, required=True):
        self.title = title
        self.required = required
        self._validators = [self.to_python]

        # Hack to maintain class attribute order in Python < 3.0
        self.counter = next(self.__class__._count)

    def attach_to_class(self, cls, name, dialect):
        self.cls = cls
        self.name = name
        self.dialect = dialect
        if self.title is None:
            # Check for None so that an empty string will skip this behavior
            self.title = name.replace('_', ' ')
        dialect.add_column(self)

    def to_python(self, value):
        """
        Convert the given string to a native Python object.
        """
        return value

    def to_string(self, value):
        """
        Convert the given Python object to a string.
        """
        return value

    # Not yet written about

    def validator(self, func):
        self._validators.append(functools.partial(func, self))
        return func

    def validate(self, value):
        """
        Validate that the given value matches the column's requirements.
        Raise a ValueError only if the given value was invalid.
        """
        for validate in self._validators:
            validate(value)


class StringColumn(Column):
    pass


class UnicodeColumn(Column):
    """A column containing Unicode data.

    Emits UTF-8 when asked to output text.
    """
    def to_string(self, value):
        return value.encode('utf-8')


class IntegerColumn(Column):
    def to_python(self, value):
        return int(value)


class FloatColumn(Column):
    def to_python(self, value):
        return float(value)


class FloatWithCommaSeparatorsColumn(Column):
    """A column containing floats with comma thousands separators.

    e.g., "1,000,000.12" -> 1000000.12

    Note that this is NOT intended to handle "Euro" floats, in which
    a comma is used as the decimal separator.
    """
    def to_python(self, value):
        if isinstance(value, basestring):
            return float(value.replace(',', ''))
        else:
            return float(value)


class BooleanColumn(Column):
    _default_bool_map = {'true': True, 'false': False}

    def __init__(self, bool_map=None, inverted_bool_map=None, *args, **kwargs):
        """
        Parameters
        ----------
        bool_map: dict-like
            Mapping of string keys to bool values. Useful if for handling
            non-standard boolean mappings, e.g. {'y': True, 'n': False}.

        inverted_bool_map: dict-like (default: inverse of `bool_map`)
            Mapping of Boolean keys to default string values, e.g.
            {True: 'yes', False: 'no}.
        """
        self._bool_map = (self._default_bool_map
                          if bool_map is None else bool_map)
        default_inverted_bool_map = {value: key for key, value
                                     in self._bool_map.iteritems()}
        self._inverted_bool_map = (default_inverted_bool_map
                                   if inverted_bool_map is None
                                   else inverted_bool_map)

        super(BooleanColumn, self).__init__(*args, **kwargs)

    def to_python(self, value):
        bool_map = self._bool_map
        str_value = str(value).lower()
        if str_value not in bool_map:
            raise ValueError("cannot map '%s' to boolean with map %s" %
                             (value, bool_map))

        return bool_map[str_value]

    def to_string(self, value):
        return self._inverted_bool_map[value]


class DecimalColumn(Column):
    """A column that contains data in the form of decimal values.

    Represented in Python by decimal.Decimal.
    """

    def to_python(self, value):
        try:
            return decimal.Decimal(value)
        except decimal.InvalidOperation as e:
            raise ValueError(str(e))


class DateTimeColumn(Column):
    """A column that contains data in the form of dates with times.

    Represented in Python by datetime.datetime.

    format
        A strptime()-style format string.
        See http://docs.python.org/library/datetime.html for details
        This string will be used as the output format for this column,
        and as the default input format as well.
    format_list
        A list of strptime()-style format strings.
        Entries in format_list will be used as alternative input formats
        for this column.
    timezone
        A pytz.timezone object.
        If non-None, datetimes parsed by this column will be localized
        into the provided timezone. If None, datetimes parsed by this
        column will be naive.
    """

    def __init__(self, format='%Y-%m-%d', format_list=None, timezone=None,
                 *args, **kwargs):
        super(DateTimeColumn, self).__init__(*args, **kwargs)
        self.format = format
        self.input_formats = set([format] + (format_list or []))
        self.timezone = timezone

    def to_python(self, value):
        """Parse a string value according to self.format.
        """
        if isinstance(value, datetime.datetime):
            return value
        elif isinstance(value, datetime.date):
            return datetime.datetime(value.year, value.month, value.day)

        for format in self.input_formats:
            try:
                dt = datetime.datetime.strptime(value, format)
                if self.timezone is not None:
                    dt = self.timezone.localize(dt)
                return dt
            except ValueError:
                continue

        msg = ("time data %s does not match any of the formats: %s" %
               (value, ", ".join(map(repr, self.input_formats))))
        raise ValueError(msg)

    def to_string(self, value):
        """Format a date according to self.format and return that as a string.
        """
        return value.strftime(self.format)


class DateColumn(DateTimeColumn):
    """
    A column that contains data in the form of dates.

    Represented in Python by datetime.date.

    See DateTimeColumn.__init__ for parameters.
    """
    def to_python(self, value):
        return super(DateColumn, self).to_python(value).date()
