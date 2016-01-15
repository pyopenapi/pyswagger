from __future__ import absolute_import
from ...errs import CycleDetectionError
from ...scan import Dispatcher
from ...spec.v2_0.parser import (
    ParameterContext,
    ResponseContext,
    PathItemContext
    )
from ...spec.v2_0.objects import (
    Parameter,
    Response,
    PathItem,
    )
from ...spec.base import NullContext
from ...utils import CycleGuard


def _merge(obj, app, creator, parser):
    """ resolve $ref, and inject/merge referenced object to self.
    This operation should be carried in a cascade manner.
    """
    result = creator(NullContext())
    result.merge(obj, parser)

    guard = CycleGuard()
    guard.update(obj)

    r = getattr(obj, '$ref')
    while r and len(r) > 0:
        ro = app.resolve(r, parser)
        if ro.__class__ != obj.__class__:
            raise TypeError('Referenced Type mismatch: {0}'.format(r))
        try:
            guard.update(ro)
        except CycleDetectionError:
            # avoid infinite loop,
            # cycle detection has a dedicated scanner.
            break

        result.merge(ro, parser)
        r = getattr(ro, '$ref')
    return result

class Merge(object):
    """ pre-merge these objects with '$ref' """

    class Disp(Dispatcher): pass

    @Disp.register([Parameter])
    def _parameter(self, _, obj, app):
        obj.update_field('final', _merge(obj, app, Parameter, ParameterContext))

    @Disp.register([Response])
    def _response(self, _, obj, app):
        obj.update_field('final', _merge(obj, app, Response, ResponseContext))

    @Disp.register([PathItem])
    def _path_item(self, _, obj, app):
        obj.merge(_merge(obj, app, PathItem, PathItemContext), PathItemContext)

