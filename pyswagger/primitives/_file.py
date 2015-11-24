from __future__ import absolute_import
from ..errs import ValidationError


class File(object):
    """ for type File
    """
    def apply_with(self, _, val, ctx):
        """ constructor

        example val:
        {
            # header values used in multipart/form-data according to RFC2388
            'header': {
                'Content-Type': 'text/plain',
                
                # according to RFC2388, available values are '7bit', '8bit', 'binary'
                'Content-Transfer-Encoding': 'binary'
            },
            filename: 'a.txt',
            data: None (or any file-like object)
        }

        :param val: dict containing file info.
        """
        self.header = val.get('header', {})
        self.data = val.get('data', None)
        self.filename = val.get('filename', '')
        if self.data == None and self.filename == '':
            raise ValidationError('should have file name or file object, not: {0}, {1}'.format(
                self.data, self.filename
            ))
