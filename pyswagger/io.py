from __future__ import absolute_import
from .primitives import PrimJSONEncoder
from .utils import deref
from pyswagger import errs
from uuid import uuid4
import six
import json
import io, codecs
import collections
import logging


logger = logging.getLogger(__name__)


class SwaggerRequest(object):
    """ Request layer
    """
    # TODO: make a new class for 'prepared' SwaggerRequest

    # option: url_netloc, replace netloc part in url, useful
    # when testing a set of Swagger APIs locally.
    opt_url_netloc = 'url_netloc'

    def __init__(self, op, params):
        """ constrcutor

        :param Operation op: the related Operation object
        :param dict params: parameter set provided by user
        :param produces: list of 'Content-Type' from parent object
        :param consumes: list of 'Accepts' from parent object
        :param authorizations: list of required authorizations from parent object
        """

        self.__op = op
        self.__p = params
        self.__url = self.__op.url
        self.__path = self.__op.path
        self.__header = {}

        # update 'accept' header section
        accepts = 'application/json'
        if accepts and self.__op.produces and accepts not in self.__op.produces:
            accepts = self.__op.produces[0]

        if accepts:
            self.__header.update({'Accept': accepts})

    def _prepare_forms(self):
        """ private function to prepare content for paramType=form
        """
        content_type = 'application/x-www-form-urlencoded'
        if self.__op.consumes and content_type not in self.__op.consumes:
            raise errs.SchemaError('unable to locate content-type: {0}'.format(content_type))

        return content_type, six.moves.urllib.parse.urlencode(self.__p['formData'])

    def _prepare_body(self):
        """ private function to prepare content for paramType=body
        """
        content_type = 'application/json'
        if self.__op.consumes and content_type not in self.__op.consumes:
            raise errs.SchemaError('unable to locate content-type: {0}'.format(content_type))

        for v in six.itervalues(self.__p['body']):
            # according to spec, payload should be one and only,
            # so we just return the first value in dict.
            return content_type, json.dumps(v, cls=PrimJSONEncoder)
        return None, None

    def _prepare_files(self, encoding):
        """ private function to prepare content for paramType=form with File
        """
        content_type = 'multipart/form-data'
        if self.__op.consumes and content_type not in self.__op.consumes:
            raise errs.SchemaError('unable to locate content-type: {0}'.format(content_type))

        boundary = uuid4().hex
        content_type += '; boundary={0}'
        content_type = content_type.format(boundary)

        # init stream
        body = io.BytesIO()
        w = codecs.getwriter(encoding)

        for k, v in self.__p['formData']:
            body.write(six.b('--{0}\r\n'.format(boundary)))

            w(body).write('Content-Disposition: form-data; name="{0}"'.format(k))
            body.write(six.b('\r\n'))
            body.write(six.b('\r\n'))

            w(body).write(v)

            body.write(six.b('\r\n'))

        # begin of file section
        for k, v in six.iteritems(self.__p['file']):
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
        """ private function to patch this request. This function
        could be called before/after preparation.

        :param dict opt: options, used options would be popped. Refer to SwaggerRequest.opt_* for details.
        """
        opt_netloc = opt.pop(SwaggerRequest.opt_url_netloc, None)
        if opt_netloc:
            scheme, netloc, path, params, query, fragment = six.moves.urllib.parse.urlparse(self.__url)
            self.__url = six.moves.urllib.parse.urlunparse(
                (scheme, opt_netloc, path, params, query, fragment)
                )

            logger.info('patching url: [{0}]'.format(self.__url))

    def prepare(self, scheme='http', handle_files=True, encoding='utf-8'):
        """ make this request ready for Clients

        :param bool handle_files: False to skip multipart/form-data encoding
        :param str encoding: encoding for body content.
        :rtype: SwaggerRequest
        """

        # combine path parameters into path
        self.__path = self.__path.format(**self.__p['path'])

        # combine path parameters into url
        self.__url = ''.join([scheme, '://', self.__url.format(**self.__p['path'])])

        # header parameters
        self.__header.update(self.__p['header'])

        # update data parameter
        content_type = None
        if self.__p['file']:
            if handle_files:
                content_type, self.__data = self._prepare_files(encoding)
            else:
                # client that can encode multipart/form-data, should
                # access form-data via data property and file from file
                # property.

                # only form data can be carried along with files,
                self.__data = self.__p['formData']

        elif self.__p['formData']:
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
        """ url of this request

        :type: str 
        """
        return self.__url

    @property
    def path(self):
        """ path of this request

        :type: str
        """
        return self.__path

    @property
    def base_path(self):
        """ base path of this request

        :type: str
        """
        return self.__op.base_path

    @property
    def query(self):
        """ query part of this request
        
        :type: dict
        """
        return self.__p['query']

    @property
    def method(self):
        """ HTTP verb of this request

        :type: str
        """
        return self.__op.method

    @property
    def header(self):
        """ header of this request

        :type: dict
        """
        return self.__header

    @property
    def data(self):
        """ data carried by this request

        :type: byte
        """
        return self.__data

    @property
    def files(self):
        """ files of this Request

        :type: dict of (name, primitives.File)
        """
        return self.__p['file']

    @property
    def schemes(self):
        """ required schemes for current Operation.

        :type: list of str
        """
        return self.__op.cached_schemes

    @property
    def _p(self):
        """ access internal placeholder of all parameters,
        for unittest/debug/internal purpose
        """
        return self.__p

    @property
    def _security(self):
        """ list of authorizations required
        
        :type: dict of list of Authorizations object.
        """
        return self.__op.security


class SwaggerResponse(object):
    """ Response layer
    """

    def __init__(self, op):
        """ constructor

        :param Operation op: the related Operation object
        """
        self.__op = op
        self.__raw = self.__data = None

        # init properties
        self.__status = None 
        self.__header = {}

    def _convert_header(self, resp, k, v):
        if resp and resp.headers and k in resp.headers:
            v = resp.headers[k]._prim_(v)

        if k in self.__header:
            self.__header[k].append(v)
        else:
            self.__header[k] = [v]

    def apply_with(self, status=None, raw=None, header=None):
        """ update header, status code, raw datum, ...etc

        :param int status: status code
        :param str raw: body content
        :param dict header: header section
        :return: return self for chaining
        :rtype: SwaggerResponse
        """

        if status != None:
            self.__status = status

        r = (deref(self.__op.responses.get(str(self.__status), None)) or
             deref(self.__op.responses.get('default', None)))

        if raw != None:
            # update 'raw'
            self.__raw = raw

            if self.__status == None:
                raise Exception('Update status code before assigning raw data')

            if r and r.schema:
                # update data from Opeartion if succeed else from responseMessage.responseModel
                self.__data = r.schema._prim_(self.raw)

        if header != None:
            if isinstance(header, (collections.Mapping, collections.MutableMapping)):
                for k, v in six.iteritems(header):
                    self._convert_header(r, k, v)
            else:
                for k, v in header:
                    self._convert_header(r, k, v)

        return self

    @property
    def status(self):
        """ status code

        :type: int
        """
        return self.__status

    @property
    def data(self):
        """ responsed data

        :type: primitives.Model
        """
        return self.__data

    @property
    def raw(self):
        """ raw response

        :type: str
        """
        return self.__raw

    @property
    def header(self):
        """ header of Response
        
        :type: dict of list, ex. {'Content-Type': [xxx, xxx]}
        """
        return self.__header

