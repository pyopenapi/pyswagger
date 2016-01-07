from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v2_0.parser import (
    SchemaContext,
    ParameterContext,
    ResponseContext,
    PathItemContext
    )
from ...spec.v2_0.objects import (
    Schema,
    Parameter,
    Response,
    PathItem,
    )
from ...utils import normalize_jr


def is_resolved(obj):
    return getattr(obj, '$ref') == None or obj.ref_obj != None

def _resolve(obj, app, parser):
    if is_resolved(obj):
        return

    r = getattr(obj, '$ref')
    ro = app.resolve(normalize_jr(r, app.url), parser)

    if not ro:
        raise ReferenceError('Unable to resolve: {0}'.format(r))
    if ro.__class__ != obj.__class__:
        raise TypeError('Referenced Type mismatch: {0}'.format(r))

    obj.update_field('ref_obj', ro)
    obj.update_field('norm_ref', normalize_jr(r, app.url))

def _merge(obj, app, ctx):
    """ resolve $ref as ref_obj, and merge ref_obj to self.
    This operation should be carried in a cascade manner.
    """

    cur = obj
    to_resolve = []
    while not is_resolved(cur):
        _resolve(cur, app, ctx)

        to_resolve.append(cur)
        cur = cur.ref_obj if cur.ref_obj else cur

    while (len(to_resolve)):
        o = to_resolve.pop()
        o.merge(o.ref_obj, ctx, exclude=['$ref'])


class Resolve(object):
    """ pre-resolve '$ref' """

    class Disp(Dispatcher): pass


    @Disp.register([Schema])
    def _schema(self, _, obj, app):
        _resolve(obj, app, SchemaContext)

    @Disp.register([Parameter])
    def _parameter(self, _, obj, app):
        _resolve(obj, app, ParameterContext)

    @Disp.register([Response])
    def _response(self, _, obj, app):
        _resolve(obj, app, ResponseContext)

    @Disp.register([PathItem])
    def _path_item(self, _, obj, app):

        # $ref in PathItem is 'merge', not 'replace'
        # we need to merge properties of others if missing
        # in current object.
        _merge(obj, app, PathItemContext)

