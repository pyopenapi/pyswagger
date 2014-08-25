from __future__ import absolute_import
from .base import BaseObj
from .prim import PrimJSONEncoder
import six
import json


class SwaggerRequest(object):
    """ Request layer
    """

    file_key = 'file_'

    def __init__(self, op, params={}, produces=None, consumes=None):
        """
        """
        self.__method = op.method
        self.__p = dict(header={}, query={}, path={}, body={}, form={}, file_={})
        self.__url = op.path

        # check for unknown parameters
        unknown = set(params.keys()) - set([p.name for p in op.parameters])
        if len(unknown):
            raise ValueError('Unknown parameters: ' + str(unknown))

        # convert params into internal types
        for p in op.parameters:
            val = params.get(p.name, None)

            # check required parameter
            if val == None and p.required:
                raise ValueError('requires parameter: ' + p.name)

            converted = p._prim_(val)
            # we could only have string for those parameter types
            if p.paramType in ('path', 'query'):
                converted = six.moves.urllib.parse.quote(str(converted))
            elif p.paramType == 'header':
                converted = str(converted)

            self.__p[p.paramType if p.type != 'File' else SwaggerRequest.file_key][p.name] = converted

        # let produces/consumes in Operation override global ones.
        produces = op.produces if op.produces else produces
        consumes = op.consumes if op.consumes else consumes
        self._set_header(op, produces, consumes)

        # combine path parameters into url
        self.__url = self.__url.format(**self.__p['path'])

        # update data parameter
        if self.__p[SwaggerRequest.file_key]:
            self.__data = self.__p[SwaggerRequest.file_key]
        elif 'Content-Type' in self.header:
            self.__data = self._encode(
                self.header['Content-Type'],
                self.__p['form'] if self.__p['form'] else self.__p['body']
            )
        else:
            self.__data = None

    def _set_header(self, op, produces, consumes):
        """ prepare header section, reference implementation:
            https://github.com/wordnik/swagger-js/blob/master/lib/swagger.js
        """
        accepts = 'application/json'
        content_type = 'application/json'

        self.__header = self.__p['header']

        if self.__p[SwaggerRequest.file_key]:
            content_type = 'multipart/form-data'
        elif self.__p['form']:
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

    def _encode(self, content_type, data):
        """
        """
        ret = ''

        if content_type == 'application/x-www-form-urlencoded':
            ret = six.moves.urllib.parse.urlencode(data)
        elif content_type == 'application/json':
            ret = json.dumps(data, cls=PrimJSONEncoder)
        elif content_type == 'multipart/form-data':
            # it's wrong to pass any file related to here.
            raise Exception('multipart/form-data encoding is not supported yet')

        return ret

    @property
    def url(self):
        """ url of this request """
        return self.__url

    @property
    def query(self):
        """ query string of this request """
        return self.__p['query']

    @property
    def method(self):
        """ HTTP verb of this request """
        return self.__method

    @property
    def header(self):
        """ header of this request """
        return self.__p['header']

    @property
    def data(self):
        """ data carried by this request """
        return self.__data

    @property
    def p(self):
        """ for unittest/debug purpose """
        return self.__p


class SwaggerResponse(object):
    """ Response layer
    """
    def __init__(self, op):
        """
        """
        self.__op = op
        self.__raw = self.__data = None

        # init properties
        self.__status = 0
        self.__header = {}

    def apply_with(self, status=None, raw=None, header=None):
        """ update header, status code, raw datum, ...etc
        """
        def _find_rm():
            """ helper function to find
            ResponseMessage object.
            """
            for rm in self.__op.responseMessages:
                if rm.code == self.status:
                    return rm
            return None

        rm = None

        if status != None:
            self.__status = status

            # looking for responseMessages in Operation object
            rm = _find_rm()
            self.__message = '' if not rm else rm.message

        if raw != None:
            if self.status == 0:
                raise Exception('Update status code before assigning raw data')

            self.__raw = raw

            # update data from Opeartion if succeed else from responseMessage.responseModel
            rm = _find_rm() if not rm else rm
            if rm and isinstance(rm.responseModel, BaseObj):
                self.__data = rm.responseModel._prim_(self.raw)

            if not self.__data:
                # when nothing works, convert raw with Operation's return type.
                self.__data = self.__op._prim_(self.__raw)

        if header != None:
            self.__header.update(header)

    def _encode(self):
        """ encode data
        """
        pass

    @property
    def status(self):
        """ status code """
        return self.__status

    @property
    def message(self):
        """ response message """
        return self.__message

    @property
    def data(self):
        """ responsed data """
        return self.__data

    @property
    def raw(self):
        """ raw response """
        return self.__raw

    @property
    def header(self):
        """ header of response """
        return self.__header

