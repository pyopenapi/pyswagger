from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v2_0.objects import (
    Operation
    )
import six


class YamlFixer(object):
    """ fix objects loaded by pyaml """

    class Disp(Dispatcher): pass

    @Disp.register([Operation])
    def _op(self, _, obj, app):
        """ convert status code in Responses from int to string
        """
        if obj.responses == None: return 

        tmp = {}
        for k, v in six.iteritems(obj.responses):
            if isinstance(k, six.integer_types):
                tmp[str(k)] = v
            else:
                tmp[k] = v
        obj.update_field('responses', tmp)

