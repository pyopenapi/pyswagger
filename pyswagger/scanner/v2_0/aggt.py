from __future__ import absolute_import
from ...scan import Dispatcher
from ...errs import CycleDetectionError
from ...spec.v2_0.objects import Schema
from ...spec.base import NullContext
from ...spec.v2_0.parser import SchemaContext
from ...utils import deref, CycleGuard
import six

def _compose(obj, guard=None):
    guard = CycleGuard() if not guard else guard

    try:
        obj = deref(obj, guard=guard)
    except CycleDetectionError:
        return

    if obj.final != None:
        return

    if obj.items != None:
        _compose(obj.items, guard)
    for v in six.itervalues(obj.properties):
        _compose(v, guard)
    for v in (obj.allOf or []):
        _compose(v, guard)

    final = Schema(NullContext())
    final.merge(obj, SchemaContext)

    # those 'allOf' are visited by the last CycleGuard,
    # we need use a new one
    guard = CycleGuard()
    stk = list(obj.allOf)
    while len(stk) > 0:
        try:
            o = deref(stk.pop(), guard=guard)
        except CycleDetectionError:
            continue
        o = o.final if o.final else o
        final.merge(o, SchemaContext, exclude=['$ref', 'allOf'])
        for n, p in six.iteritems(o.properties):
            if n in obj.properties:
                continue
            final.properties[n] = p
        stk.extend(o.allOf or [])
    obj.update_field('final', final)


class Aggregate(object):
    """ aggregate 'allOf',
    This scanner should be run after resolving '$ref'
    """

    # TODO: rework SwaggerPrimitive.produce

    class Disp(Dispatcher): pass

    @Disp.register([Schema])
    def _schema(self, path, obj, _):
        _compose(obj)
