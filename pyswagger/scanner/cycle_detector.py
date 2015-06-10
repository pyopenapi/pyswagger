from __future__ import absolute_import
from ..utils import normalize_jr, walk
from ..scan import Dispatcher
from ..spec.v2_0.objects import (
    Schema,
    Parameter,
    Response,
    PathItem,
    )
import functools
import six

def _out(app, prefix, path):
    obj = app.resolve(normalize_jr(path, prefix))
    r = getattr(obj, 'norm_ref')
    return [r] if r else []

def _schema_out_obj(obj, out=None):
    out = [] if out == None else out

    for o in six.itervalues(obj.properties):
        out = _schema_out_obj(o, out)

    for o in obj.allOf:
        out = _schema_out_obj(o, out)

    if isinstance(obj.additionalProperties, Schema):
        out = _schema_out_obj(obj.additionalProperties, out)

    if obj.items:
        out = _schema_out_obj(obj.items, out)

    r = getattr(obj, 'norm_ref')
    if r:
        out.append(r)

    return out

def _schema_out(app, path):
    obj = app.resolve(normalize_jr(path, '#/definitions'))
    return [] if obj == None else _schema_out_obj(obj)


class CycleDetector(object):
    """ circular detector """

    class Disp(Dispatcher): pass

    def __init__(self):
        self.cycles = {
            'schema':[],
            'parameter':[],
            'response':[],
            'path_item':[]
        }

    @Disp.register([Schema])
    def _schema(self, path, _, app):
        self.cycles['schema'] = walk(
            path,
            functools.partial(_schema_out, app),
            self.cycles['schema']
        )

    @Disp.register([Parameter])
    def _parameter(self, path, _, app):
         self.cycles['parameter'] = walk(
            path,
            functools.partial(_out, app, '#/parameters'),
            self.cycles['parameter']
        )

    @Disp.register([Response])
    def _response(self, path, _, app):
        self.cycles['response'] = walk(
            path,
            functools.partial(_out, app, '#/responses'),
            self.cycles['response']
        )

    @Disp.register([PathItem])
    def _path_item(self, path, _, app):
        self.cycles['path_item'] = walk(
            path,
            functools.partial(_out, app, '#/paths'),
            self.cycles['path_item']
        )

