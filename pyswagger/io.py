from __future__ import absolute_import


class SwaggerRequest(object):
    """ Request layer
    """
    def __init__(self, op, params={}, produces=None, consumes=None):
        """
        """
        self.__verb = op.method
        self.__p = dict(header={}, query={}, path={}, body={}, form={})
        self.__url = op.path
        self.__has_file = False

        # check for unknown parameters
        unknown = set(params.keys()) - set([p.name for p in op.parameters])
        if len(unknown):
            raise ValueError('Unknown parameters: ' + str(unknown))

        # let produces/consumes in Operation override global ones.
        produces = op.produces if op.produces else produces
        consumes = op.consumes if op.consumes else consumes
        self.set_header(op, produces, consumes)

        # convert params into internal types
        for p in op.parameters:
            val = params.get(p.name, None)

            # check required parameter
            if val == None and p.required:
                raise ValueError('requires parameter: ' + p.name)

            if p.type == 'File' and val:
                self.__has_file = True

            self.__p[p.paramType][p.name] = p._prim_(val)

        # combine path parameters into url
        self.__url = self.__url.format(**self.__p['path'])

        # update data parameter
        self.__data = self.__p['form'] if self.__p['form'] else self.__p['body']

    def set_header(self, op, produces, consumes):
        """ prepare header section, reference implementation:
            https://github.com/wordnik/swagger-js/blob/master/lib/swagger.js
        """
        accepts = 'application/json'
        content_type = 'application/json'

        self.__header = self.__p['header']

        if self.__p['form']:
            if self.__has_file:
                content_type = 'multipart/form-data'
            else:
                content_type = 'application/x-www-form-urlencoded'
        elif op.method == 'DELETE':
            self.__p['body'] = {}

        if content_type and consumes and content_type not in consumes:
            content_type = consumes[0]
        if accepts and produces and accepts not in produces:
            accepts = produces[0]

        if (content_type and self.__p['body']) or content_type == 'application/x-www-form-urlencoded':
            self.__header['Content-Type'] = content_type 
        if accepts:
            self.__header['Accept'] = accepts

    @property
    def url(self):
        """ url of this request """
        return self.__url

    @property
    def query(self):
        """ query string of this request """
        return self.__p['query']

    @property
    def verb(self):
        """ HTTP verb of this request """
        return self.__verb

    @property
    def header(self):
        """ header of this request """
        return self.__p['header']

    @property
    def data(self):
        """ data carried by this request """
        return self.__data


class SwaggerResponse(object):
    """ Response layer
    """
    def __init__(self, op):
        """
        """
        self.__op = op

    def apply(self, **kwargs):
        """
        """
        pass

    @property
    def status_code(self):
        """ status code """

    @property
    def message(self):
        """ error message when failed """

    @property
    def data(self):
        """ responsed data """

    @property
    def raw(self):
        """ raw response """

