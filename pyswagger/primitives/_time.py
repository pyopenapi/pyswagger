from __future__ import absolute_import
from ..utils import from_iso8601
import datetime
import six


class Time(object):
    """ Base of Datetime & Date
    """

    def __str__(self):
        return str(self.to_json())

    def to_json(self):
        # according to
        #   https://github.com/wordnik/swagger-spec/issues/95
        return self.v.isoformat()


class Date(Time):
    """ for string type, date format
    """

    def apply_with(self, _, v, ctx):
        """ constructor

        :param v: things used to constrcut date
        :type v: timestamp in float, datetime.date object, or ISO-8601 in str
        """
        self.v = None
        if isinstance(v, float):
            self.v = datetime.date.fromtimestamp(v)
        elif isinstance(v, datetime.date):
            self.v = v
        elif isinstance(v, six.string_types):
            self.v = from_iso8601(v).date()
        else:
            raise ValueError('Unrecognized type for Date: ' + str(type(v)))


class Datetime(Time):
    """ for string type, datetime format
    """

    def apply_with(self, _, v, ctx):
        """ constructor

        :param v: things used to constrcut date
        :type v: timestamp in float, datetime.datetime object, or ISO-8601 in str
        """
        self.v = None
        if isinstance(v, float):
            self.v = datetime.datetime.utcfromtimestamp(v)
        elif isinstance(v, datetime.datetime):
            self.v = v
        elif isinstance(v, six.string_types):
            self.v = from_iso8601(v)
        else:
            raise ValueError('Unrecognized type for Datetime: ' + str(type(v)))


