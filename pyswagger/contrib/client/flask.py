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
        :param auth pyswagger.SwaggerSecurity: auth info holder
        """
        super(FlaskTestClient, self).__init__(auth)
        self.__client = client

    def request(self, req_and_resp, opt={}):
        """
        """
        req, resp = super(FlaskTestClient, self).request(req_and_resp, opt)

        # apply request-related options before preparation.
        req.prepare(scheme=self.prepare_schemes(req).pop(), handle_files=False)
        req._patch(opt)

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
            path=req.path,
            query_string=req.query,
            method=req.method.upper(),
            headers=req.header.items(),
            data=data
            )

        # convert to SwaggerResponse
        resp.apply_with(
            status=r.status_code,
            header=r.headers.items(),
            raw=r.data
        )

        return resp

