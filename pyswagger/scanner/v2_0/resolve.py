from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v2_0.objects import (
    Schema,
    Parameter,
    Response,
    PathItem,
    )
from ...utils import jp_split, jp_compose


class Resolve(object):
    """ pre-resolve '$ref' """

    class Disp(Dispatcher): pass

    @Disp.register([Schema, Parameter, Response, PathItem])
    def _resolve(self, path, obj, app):
        r = getattr(obj, '$ref')
        if r == None:
            return

        try:
            ro = app.resolve(r)
        except Exception:
            ps = jp_split(path)[:2]
            ps.append(r)
            ro = app.resolve(jp_compose(ps))

        if not ro:
            raise ReferenceError('Unable to resolve: {0}'.format(r))
        if ro.__class__ != obj.__class__:
            raise TypeError('Referenced Type mismatch: {0}'.format(r))

        obj.update_field('ref_obj', ro)

