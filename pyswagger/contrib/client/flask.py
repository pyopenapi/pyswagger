from __future__ import absolute_import
from ...core import BaseClient
from werkzeug.datastructures import FileStorage
import six


class FlaskTestClient(BaseClient):
    """ Flask Test Client
    """

    __schemes__ = set(['http', 'https'])

    def __init__(self, client, auth=None):
        """ contructor

        :param client: a testing client created by flask.test_client()
        :param auth pyswagger.Security: auth info holder
        """
        super(FlaskTestClient, self).__init__(auth)
        self.__client = client

    def request(self, req_and_resp, opt=None, headers=None):
        """
        """

        # make sure all prepared state are clean before processing
        req, resp = req_and_resp
        req.reset()
        resp.reset()

        opt = opt or {}
        req, resp = super(FlaskTestClient, self).request((req, resp), opt)

        # apply request-related options before preparation.
        req.prepare(scheme=self.prepare_schemes(req), handle_files=False)
        req._patch(opt)

        composed_headers = self.compose_headers(req, headers, opt)

        # prepare data, flask's data is composed of form and file
        if req.files:
            data = {}
            # form
            data.update(req._p['formData'])
            # file
            for k, v in six.iteritems(req.files):
                if isinstance(v, list):
                    data[k] = []
                    for vv in v:
                        data[k].append(FileStorage(
                            name=k,
                            filename=vv.filename,
                            stream=vv.data
                        ))
                else:
                    data[k] = FileStorage(
                        name=k,
                        filename=v.filename,
                        stream=v.data
                    )

        else:
            data = req.data if req._p['body'] else req._p['formData']

        r = self.__client.open(
            path=req.url,
            query_string=req.query,
            method=req.method.upper(),
            headers=composed_headers,
            data=data
            )

        # convert to Response
        resp.apply_with(
            status=r.status_code,
            header=r.headers.items(),
            raw=r.data
        )

        return resp

