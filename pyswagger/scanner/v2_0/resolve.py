from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v2_0.objects import (
    Schema,
    Parameter,
    Response,
    PathItem,
    )


class Resolve(object):
    """ pre-resolve '$ref' """

    class Disp(Dispatcher): pass

    @Disp.register([Schema, Parameter, Response, PathItem])
    def _resolve(self, _, obj, app):
        r = getattr(obj, '$ref')
        if r == None:
            return

        ro = app.resolve(r)
        if not ro:
            raise ReferenceError('Unable to resolve: {0}'.format(r))
        if ro.__class__ != obj.__class__:
            raise TypeError('Referenced Type mismatch: {0}'.format(r))

        obj.update_field('ref_obj', ro)

