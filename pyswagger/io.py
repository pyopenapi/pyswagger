from __future__ import absolute_import
from .base import BaseObj
from .primitives import PrimJSONEncoder
from uuid import uuid4
import six
import json
import io, codecs


class SwaggerRequest(object):
    """ Request layer
    """

    # options
    opt_url_netloc = 'url_netloc'

    def __init__(self, op, params={}, produces=None, consumes=None, authorizations=None):
        """
        """
        self.__method = op.method
        self.__p = dict(header={}, query={}, path={}, body={}, form={}, File={})
        self.__url = op._parent_.basePath + op.path
        self.__is_prepared = False
        self.__header = {}

        # TODO: this part can be resolved once by using scanner.
        # let produces/consumes/authorizations in Operation override global ones.
        self.__produces = op.produces if op.produces else produces
        self.__consumes = op.consumes if op.consumes else consumes
        self.__authorizations = op.authorizations if op.authorizations else authorizations

        # check for unknown parameters
        unknown = set(params.keys()) - set([p.name for p in op.parameters])
        if len(unknown):
            raise ValueError('Unknown parameters: ' + str(unknown))

        # convert params into internal types
        for p in op.parameters:
            val = params.get(p.name, None)

            # check required parameter
            val = p.defaultValue if val == None else val
            if val == None and p.required:
                raise ValueError('requires parameter: ' + p.name)

            converted = p._prim_(val)
            # we could only have string for those parameter types
            if p.paramType in ('path', 'query'):
                converted = six.moves.urllib.parse.quote(str(converted))
            elif p.paramType == 'header':
                converted = str(converted)

            self.__p[p.paramType if p.type != 'File' else 'File'][p.name] = converted

        # update 'accept' header section
        accepts = 'application/json'
        if accepts and self.__produces and accepts not in self.__produces:
            accepts = self.__produces[0]

        if accepts:
            self.__header.update({'Accept': accepts})

    def _prepare_forms(self):
        """
        """
        content_type = 'application/x-www-form-urlencoded'
        if self.__consumes and content_type not in self.__consumes:
            raise ValueError('unable to locate content-type: {0}'.format(content_type))

        return content_type, six.moves.urllib.parse.urlencode(self.__p['form'])

    def _prepare_body(self):
        """
        """
        content_type = 'application/json'
        if self.__consumes and content_type not in self.__consumes:
            raise ValueError('unable to locate content-type: {0}'.format(content_type))

        return content_type, json.dumps(
            self.__p['body'], cls=PrimJSONEncoder)

    def _prepare_files(self, encoding):
        """
        """
        content_type = 'multipart/form-data'
        if self.__consumes and content_type not in self.__consumes:
            raise ValueError('unable to locate content-type: {0}'.format(content_type))

        boundary = uuid4().hex
        content_type += '; boundary={0}'
        content_type = content_type.format(boundary)

        # init stream
        body = io.BytesIO()
        w = codecs.getwriter(encoding)

        for k, v in six.iteritems(self.__p['form']):
            body.write(six.b('--{0}\r\n'.format(boundary)))

            w(body).write('Content-Disposition: form-data; name="{0}"'.format(k))
            body.write(six.b('\r\n'))
            body.write(six.b('\r\n'))

            w(body).write(v)

            body.write(six.b('\r\n'))

        # begin of file section
        for k, v in six.iteritems(self.__p['File']):
            body.write(six.b('--{0}\r\n'.format(boundary)))

            # header
            w(body).write('Content-Disposition: form-data; name="{0}"; filename="{1}"'.format(k, v.filename))
            body.write(six.b('\r\n'))
            if 'Content-Type' in v.header:
                w(body).write('Content-Type: {0}'.format(v.header['Content-Type']))
                body.write(six.b('\r\n'))
            if 'Content-Transfer-Encoding' in v.header:
                w(body).write('Content-Transfer-Encoding: {0}'.format(v.header['Content-Transfer-Encoding']))
                body.write(six.b('\r\n'))
            body.write(six.b('\r\n'))

            # body
            if not v.data:
                with open(v.filename, 'rb') as f:
                    body.write(f.read())
            else:
                data = v.data.read()
                if isinstance(data, six.text_type):
                    w(body).write(data)
                else:
                    body.write(data)

            body.write(six.b('\r\n'))

        # final boundary
        body.write(six.b('--{0}--\r\n'.format(boundary)))

        return content_type, body.getvalue()

    def _patch(self, opt={}):
        """
        """
        opt_netloc = opt.pop(SwaggerRequest.opt_url_netloc, None)
        if opt_netloc:
            scheme, netloc, path, params, query, fragment = six.moves.urllib.parse.urlparse(self.__url)    
            self.__url = six.moves.urllib.parse.urlunparse(
                (scheme, opt_netloc, path, params, query, fragment)
                )

        # if already prepared, prepare again to apply 
        # those patches.
        if self.__is_prepared:
            self.prepare()

    def prepare(self, handle_files=True, encoding='utf-8'):
        """ make this request ready for any Client
        """

        self.__is_prepared = True

        # combine path parameters into url
        self.__url = self.__url.format(**self.__p['path'])

        # header parameters
        self.__header.update(self.__p['header'])

        # update data parameter
        content_type = None
        if self.__p['File']:
            if handle_files:
                content_type, self.__data = self._prepare_files(encoding)
            else:
                # client that can encode multipart/form-data, should
                # access form-data via data property and file from file
                # property.

                # only form data can be carried along with files,
                self.__data = self.__p['form']

        elif self.__p['form']:
            content_type, self.__data = self._prepare_forms()
        elif self.__p['body']:
            content_type, self.__data = self._prepare_body()
        else:
            self.__data = None

        if content_type:
            self.__header.update({'Content-Type': content_type})

        return self
    

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
        return self.__header

    @property
    def data(self):
        """ data carried by this request """
        return self.__data

    @property
    def files(self):
        """ files of this request """
        return self.__p['File']

    @property
    def _p(self):
        """ for unittest/debug/internal purpose """
        return self.__p

    @property
    def _auths(self):
        """ list of authorizations required """
        return self.__authorizations


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
            for k, v in six.iteritems(header):
                # split v into comma separated list
                v = str(v).split(',')

                if k in self.__header:
                    self.__header[k].extend(v)
                else:
                    self.__header[k] = v

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

