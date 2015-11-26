from __future__ import absolute_import
from ..errs import ValidationError, SchemaError
import functools
import six


class Array(list):
    """ for array type, or parameter when allowMultiple=True
    """

    def __init__(self):
        """ v: list or string_types
        """
        super(Array, self).__init__()
        self.__collection_format = 'csv'

    def apply_with(self, obj, val, ctx):
        """
        """
        self.__collection_format = getattr(obj, 'collectionFormat', 'csv')

        if isinstance(val, six.string_types):
            if self.__collection_format == 'csv':
                val = val.split(',')
            elif self.__collection_format == 'ssv':
                val = val.split(' ')
            elif self.__collection_format == 'tsv':
                val = val.split('\t')
            elif self.__collection_format == 'pipes':
                val = val.split('|')
            else:
                raise SchemaError("Unsupported collection format '{0}' when converting array: {1}".format(self.__collection_format, val))

        val = set(val) if obj.uniqueItems else val

        if obj.items and len(val):
            self.extend(map(functools.partial(ctx['factory'].produce, obj.items), val))
            val = []

        # init array as list
        if obj.minItems and len(self) < obj.minItems:
            raise ValidationError('Array should be more than {0}, not {1}'.format(obj.minItems, len(self)))
        if obj.maxItems and len(self) > obj.maxItems:
            raise ValidationError('Array should be less than {0}, not {1}'.format(obj.maxItems, len(self)))

        return val

    def __str__(self):
        """ array primitives should be for 'path', 'header', 'query'.
        Therefore, this kind of convertion is reasonable.

        :return: the converted string
        :rtype: str
        """
        def _conv(p):
            s = ''
            for v in self:
                s = ''.join([s, p if s else '', str(v)])
            return s
    
        if self.__collection_format == 'csv':
            return _conv(',')
        elif self.__collection_format == 'ssv':
            return _conv(' ')
        elif self.__collection_format == 'tsv':
            return _conv('\t')
        elif self.__collection_format == 'pipes':
            return _conv('|')
        else:
            raise SchemaError('Unsupported collection format when converting to str: {0}'.format(self.__collection_format))

    def to_url(self):
        """ special function for handling 'multi',
        refer to Swagger 2.0, Parameter Object, collectionFormat
        """
        if self.__collection_format == 'multi':
            return [str(s) for s in self]
        else:
            return [str(self)]


