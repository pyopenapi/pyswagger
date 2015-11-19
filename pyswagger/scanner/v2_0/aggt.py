from __future__ import absolute_import
from ...scan import Dispatcher
from ...errs import CycleDetectionError
from ...spec.v2_0.objects import Schema
from ...spec.base import NullContext
from ...spec.v2_0.parser import SchemaContext
from ...utils import deref, CycleGuard
import six


class Aggregate(object):
    """ aggregate 'allOf',
    This scanner should be run after resolving '$ref'
    """

    # TODO: rework SwaggerPrimitive.produce

    class Disp(Dispatcher): pass

    @Disp.register([Schema])
    def _schema(self, _, obj, app):
        if obj.final != None:
            return

        guard = CycleGuard()
        try:
            obj = deref(obj, guard=guard)
        except CycleDetectionError:
            pass

        if obj.allOf == None:
            return

        final = Schema(NullContext())
        final.update_field('additionalProperties', obj.additionalProperties)
        final.merge(obj, SchemaContext)

        stk = list(obj.allOf)
        while len(stk) > 0:
            o = deref(stk.pop(), guard=guard)
            final.merge(o, SchemaContext, exclude=['$ref', 'allOf'])
            for n, p in six.iteritems(o.properties):
                if n in obj.properties:
                    continue
                final.properties[n] = p

            stk.extend(o.allOf or [])

        obj.update_field('final', final)
