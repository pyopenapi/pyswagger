from __future__ import absolute_import
import uuid
import six


class UUID(object):
    """ wrapper of uuid.UUID
    """

    def __str__(self):
        return str(self.v)

    def to_json(self):
        return str(self.v)

    def apply_with(self, _, val, ctx):
        """ constructor

        :param val: things used to construct uuid
        :type val: uuid as byte, string, or uuid.UUID
        """
        if isinstance(val, uuid.UUID):
            self.v = val
        elif isinstance(val, six.string_types):
            try:
                self.v = uuid.UUID(val)
            except ValueError:
                self.v = uuid.UUID(bytes=val)
        elif isinstance(val, six.binary_type):
            # TODO: how to support bytes_le?
            self.v = uuid.UUID(bytes=val)
        else:
            raise ValueError('Unrecognized type for UUID: ' + str(type(v)))
