from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v2_0.objects import PathItem, Operation
from ...spec.v2_0.parser import PathItemContext
from ...utils import jp_split


class PatchOperation(object):
    """ 
    - produces/consumes in Operation object should override those in Swagger object.
    - parameters in Operation object should override those in PathItem object.
    - fulfill Operation.method, which is a pyswagger-only field.
    """

    class Disp(Dispatcher): pass

    @Disp.register([Operation])
    def _operation(self, path, obj, app):
        # TODO: test case
        # produces/consumes
        obj.produces = app.root.produces if not len(obj.produces) else obj.produces
        obj.consumes = app.root.consumes if not len(obj.consumes) else obj.consumes

        # combine parameters from PathItem
        for p in obj._parent_.parameters:
            for pp in obj.parameters:
                if p.name == pp.name:
                    break
            else:
                obj.parameters.append(p)

    @Disp.register([PathItem])
    def _path_item(self, path, obj, app):
        # TODO: test case
        url = app.host + app.basePath + jp_split(path)[-1]
        for c in PathItemContext.__swagger_child__:
            o = getattr(obj, c[0])
            if isinstance(o, Operation):
                # url
                o.update_field('url', url)
                # http method
                o.update_field('method', c[0]) 

