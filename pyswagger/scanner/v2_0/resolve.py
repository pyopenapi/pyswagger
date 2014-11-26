from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v2_0.objects import (
    Schema,
    Parameter,
    Response,
    PathItem,
    )
from ...utils import jp_compose


# TODO: test case

def _resolve(obj, app, prefix):
    r = getattr(obj, '$ref')
    if r == None:
        return

    try:
        ro = app.resolve(r)
    except Exception:
        ro = app.resolve(jp_compose(r, base=prefix)) 

    if not ro:
        raise ReferenceError('Unable to resolve: {0}'.format(r))
    if ro.__class__ != obj.__class__:
        raise TypeError('Referenced Type mismatch: {0}'.format(r))

    obj.update_field('ref_obj', ro)


class Resolve(object):
    """ pre-resolve '$ref' """

    class Disp(Dispatcher): pass


    @Disp.register([Schema, Parameter, Response, PathItem])
    def _schema(self, _, obj, app):
        _resolve(obj, app, '#/definitions')

    def _parameter(self, _, obj, app):
        _resolve(obj, app, '#/parameters')

    def _response(self, _, obj, app):
        _resolve(obj, app, '#/responses')

    def _path_item(self, _, obj, app):
        _resolve(obj, app, '#/paths')

