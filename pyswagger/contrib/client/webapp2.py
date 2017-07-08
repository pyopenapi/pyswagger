from __future__ import absolute_import
from ...core import BaseClient
import webapp2
import six
import sys


class Webapp2TestClient(BaseClient):
    """ Webapp2 Test Client
    """

    __schemes__ = set(['http', 'https'])

    def __init__(self, app, auth=None, keep_cookie=False, **kw):
        """ constructor

        :param app webapp2.WSGIApplication: the WSGI application to be tested
        :param auth pyswagger.Security: auth info holder
        :param keep_cookie bool: keep cookie as session or not
        """
        super(Webapp2TestClient, self).__init__(auth)

        #
        # if webapp2 finally support python 3, please submit an issue to remove this check
        #
        if sys.version_info[0] > 2:
            raise Exception('webapp2 only support python 2.x')

        self.__app = app
        self.__keep_cookie = keep_cookie
        self.__cookie = None
        self.__kw = kw

    def request(self, req_and_resp, opt={}):
        """
        """

        # make sure all prepared state are clean before processing
        req, resp = req_and_resp
        req.reset()
        resp.reset()

        req, resp = super(Webapp2TestClient, self).request((req, resp), opt)

        req.prepare(scheme=self.prepare_schemes(req), handle_files=True)
        req._patch(opt)

        url = req.url
        if req.query:
            if url[-1] not in ('?', '&'):
                url += '&' if ('?' in url) else '?'
            url += six.moves.urllib.parse.urlencode(req.query)

        # initiate an request every time
        _req = webapp2.Request.blank(
            url,
            headers=req.header.items(),
            POST=req.data,
            **self.__kw
        )
        _req.method = req.method.upper()
        if self.__cookie:
            _req.headers['Cookie'] = self.__cookie

        # perform the request
        _resp = _req.get_response(self.__app)

        # prepare response
        resp.apply_with(
            status=_resp.status_int,
            raw=_resp.body,
            header=_resp.headerlist,
            )

        if self.__keep_cookie:
            if 'Set-Cookie' in _resp.headers:
                self.__cookie = _resp.headers['Set-Cookie']

        return resp

