from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v2_0.objects import (
    Schema
    )
import six


class Validate(object):
    """
    """
    class Disp(Dispatcher): pass

    def __init__(self):
        self.errs = []

    @Disp.result
    def result(self, result):
        """ aggregate errors """
        if result and len(result[2]) > 0:
            self.errs.extend([((result[0], result[1]), err) for err in result[2]])

    @Disp.register([Schema])
    def _validate_schema(self, path, obj, _):
        errs = []

        for v in obj.required:
            if v in obj.properties and obj.properties[v].readOnly:
                errs.append('ReadOnly property in required list: {0}'.format(v))
            # TODO: validator runs before Resolver, so we can't go through all 'allOf'
            #       Schema objects to look for the 'required' property, it's a limitation now.
            #
            #       Maybe we need to consider making another validator runs after Resolver.

        return path, obj.__class__.__name__, errs
