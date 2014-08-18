from __future__ import absolute_import


class SwaggerRequest(object):
    """ Request layer
    """
    def __init__(self, op, params):
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

        self.set_header(op)

        # convert params into internal types
        for p in op.parameters:
            val = params.get(p.name, None)

            if p.type == 'File' and val:
                self.__has_file = True

            self.__p[p.paramType][p.name] = p._prim_(val)

        # combine path parameters into url
        self.__url = self.__url.format(**self.__p['path'])

        # update data parameter
        self.__data = self.__p['form'] if self.__p['form'] else self.__p['body']

    def set_header(self, op):
        """ prepare header section, reference implementation:
            https://github.com/wordnik/swagger-js/blob/master/lib/swagger.js
        """
        accepts = 'application/json'
        consumes = 'application/json'

        self.__header = self.__p['header']

        if self.__p['form']:
            if self.__has_file:
                consumes = 'multipart/form-data'
            else:
                consumes = 'application/x-www-form-urlencoded'
        elif op.method == 'DELETE':
            self.__p['body'] = {}

        if consumes and op.consumes and consumes not in op.consumes:
            consumes = op.consumes[0]
        if accepts and op.produces and accepts not in op.produces:
            accepts = op.produces[0]

        if (consumes and self.__p['body']) or consumes == 'application/x-www-form-urlencoded':
            self.__header['Content-Type'] = consumes
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

    @property
    def status_code(self):
        """ status code """



