from __future__ import absolute_import
from pyswagger import App
from pyswagger.primitives import Renderer, File
from .utils import get_test_data_folder
from ..utils import from_iso8601
from os import path
from validate_email import validate_email
import unittest
import six
import uuid
import time
import string
import datetime
import json
import io


class StringTestCase(unittest.TestCase):
    """ render 'string' types """
    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'string')
        ))
        kls.rnd = Renderer()

    def test_string(self):
        opt = self.rnd.default()
        for _ in six.moves.xrange(50):
            s = self.rnd.render(
                self.app.resolve('#/definitions/string.1'),
                opt=opt
            )
            self.assertTrue(isinstance(s, six.string_types), 'should be string, not {0}'.format(s))
            self.assertTrue(len(s) <= opt['max_str_length'])

    def test_string_min_max(self):
        obj = self.app.resolve('#/definitions/string.2')
        for _ in six.moves.xrange(50):
            s = self.rnd.render(
                obj,
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(s, six.string_types), 'should be string, not {0}'.format(s))
            self.assertTrue(
                len(s) <= obj.maxLength and len(s) >= obj.minLength,
                'should be between {0}-{1}, not {2}'.format(obj.minLength, obj.maxLength, len(s))
            )

    def test_password(self):
        opt = self.rnd.default()
        for _ in six.moves.xrange(50):
            s = self.rnd.render(
                self.app.resolve('#/definitions/password.1'),
                opt=opt
            )
            self.assertTrue(isinstance(s, six.string_types), 'should be string, not {0}'.format(s))
            self.assertTrue(len(s) <= opt['max_str_length'])

    def test_uuid(self):
        u = self.rnd.render(
            self.app.resolve('#/definitions/uuid.1'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(u, uuid.UUID), 'should be UUID, not {0}'.format(u))

    def test_byte(self):
        b64s = list(string.digits) + list(string.ascii_letters) + ['/', '+']
        bt = self.rnd.render(
            self.app.resolve('#/definitions/byte.1'),
            opt=self.rnd.default()
        )
        # verify it's base64
        self.assertTrue(len(bt) % 4 == 0, 'not a base64 string, {0}'.format(bt))
        decoded = bt.decode('utf-8')
        idx = decoded.find('=')
        for v in decoded[:idx if idx != -1 else len(decoded)]:
            self.assertTrue(v in b64s, 'should be an allowed char, not {0}'.format(v))

    def test_date(self):
        d = self.rnd.render(
            self.app.resolve('#/definitions/date.1'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(d, datetime.date), 'should be a datetime.date, not {0}'.format(d))

    def test_datetime(self):
        d = self.rnd.render(
            self.app.resolve('#/definitions/datetime.1'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(d, datetime.datetime), 'should be a datetime.date, not {0}'.format(d))

    def test_email(self):
        for _ in six.moves.xrange(50):
            e = self.rnd.render(
                self.app.resolve('#/definitions/email.1'),
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, six.string_types), 'should be string, not {0}'.format(e))
            self.assertTrue(validate_email(e), 'should be a email, not {0}'.format(e))


class OtherTestCase(unittest.TestCase):
    """ render 'integer/float/bool' types """
    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'other')
        ))
        kls.rnd = Renderer()

    def test_integer(self):
        for _ in six.moves.xrange(50):
            i = self.rnd.render(
                self.app.resolve('#/definitions/integer.1'),
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(i, six.integer_types), 'should be integer, not {0}'.format(i))
            self.assertTrue(i <= 50, 'should be less than 50, not {0}'.format(i))
            self.assertTrue(i >= 10, 'should be greater than 10, not {0}'.format(i))
            self.assertTrue((i % 5) == 0, 'should be moduleable by 5, not {0}'.format(i))

    def test_integer_without_format(self):
        for _ in six.moves.xrange(50):
            i = self.rnd.render(
                self.app.resolve('#/definitions/integer.2'),
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(i, six.integer_types), 'should be integer, not {0}'.format(i))

    def test_float(self):
        for _ in six.moves.xrange(50):
            f = self.rnd.render(
                self.app.resolve('#/definitions/float.1'),
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(f, float), 'should be float, not {0}'.format(f))
            self.assertTrue(f <= 100, 'should be less than 100, not {0}'.format(f))
            self.assertTrue(f >= 50, 'should be greater than 50, not {0}'.format(f))
            self.assertTrue((f % 5) == 0, 'should be moduleable by 5, not {0}'.format(f))

    def test_float_without_format(self):
        for _ in six.moves.xrange(50):
            f = self.rnd.render(
                self.app.resolve('#/definitions/float.2'),
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(f, float), 'should be float, not {0}'.format(f))

    def test_bool(self):
        b = self.rnd.render(
            self.app.resolve('#/definitions/bool.1'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(b, bool), 'should be bool, not {0}'.format(b))

    def test_enum_string(self):
        obj = self.app.resolve('#/definitions/enum.string')
        for _ in six.moves.xrange(50):
            e = self.rnd.render(
                obj,
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, six.string_types), 'should be a string, not {0}'.format(e))
            self.assertTrue(e in obj.enum, 'should be one of {0}, not {1}'.format(obj.enum, e))

        opt = self.rnd.default()
        # value from enum should not validate
        opt['max_str_length'] = 1
        for _ in six.moves.xrange(50):
            e = self.rnd.render(
                obj,
                opt=opt
            )

    def test_enum_integer(self):
        obj = self.app.resolve('#/definitions/enum.integer')
        for _ in six.moves.xrange(50):
            e = self.rnd.render(
                obj,
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, six.integer_types), 'should be a integer, not {0}'.format(e))
            self.assertTrue(e in obj.enum, 'should be one of {0}, not {1}'.format(obj.enum, e))

    def test_enum_boolean(self):
        obj = self.app.resolve('#/definitions/enum.boolean')
        for _ in six.moves.xrange(50):
            e = self.rnd.render(
                obj,
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, bool), 'should be a boolean, not {0}'.format(e))
            self.assertTrue(e in obj.enum, 'should be one of {0}, not {1}'.format(obj.enum, e))

    def test_enum_uuid(self):
        obj = self.app.resolve('#/definitions/enum.uuid')
        for _ in six.moves.xrange(50):
            e = self.rnd.render(
                obj,
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, uuid.UUID), 'should be an uuid, not {0}'.format(e))
            self.assertTrue(str(e) in obj.enum, 'should be an element in enum, not {0}'.format(e))

    def test_enum_date(self):
        obj = self.app.resolve('#/definitions/enum.date')
        for _ in six.moves.xrange(50):
            e = self.rnd.render(
                obj,
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, datetime.date), 'should be a datetime.date, not {0}'.format(e))
            self.assertTrue(e.isoformat() in obj.enum, 'should be an element in enum, not {0}'.format(e))

    def test_enum_datetime(self):
        # note: can't compare non-timezone datetime with timezone'd' datetime
        # note: isoformat() of datetime is not unique
        # therefore, I compare their timestamp here.
        obj = self.app.resolve('#/definitions/enum.datetime')
        es = [time.mktime(from_iso8601(t).timetuple()) for t in obj.enum]
        for _ in six.moves.xrange(50):
            e = self.rnd.render(
                obj,
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, datetime.datetime), 'should be a datetime.datetime, not {0}'.format(e))
            self.assertTrue(time.mktime(e.timetuple()) in es, 'should be an element in enum, not {0}'.format(e))

    def test_enum_email(self):
        """ always trust enum when rendering """
        obj = self.app.resolve('#/definitions/enum.email')
        for _ in six.moves.xrange(50):
            e = self.rnd.render(
                obj,
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, six.string_types), 'should be a string, not {0}'.format(str(type(e))))
            self.assertTrue(e in obj.enum, 'should be an element in enum, not {0}'.format(e))


class ArrayTestCase(unittest.TestCase):
    """ render 'array' types """
    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'array')
        ))
        kls.rnd = Renderer()

    def test_array_of_email(self):
        """ basic case with email """
        a = self.rnd.render(
            self.app.resolve('#/definitions/array.email'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(a, list), 'should be a list, not {0}'.format(a))
        self.assertTrue(len(a) <= 50, 'should be less than 50, not {0}'.format(len(a)))
        for v in a:
            self.assertTrue(validate_email(v), 'should be an email, not {0}'.format(v))

    def test_array_allOf(self):
        """ lots of allOf """
        a = self.rnd.render(
            self.app.resolve('#/definitions/array.allOf'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(a, list), 'should be a list, not {0}'.format(a))
        self.assertTrue(len(a) <= 50 and len(a) >= 10, 'should be less than 50 and more than 10, not {0}'.format(len(a)))
        for v in a:
            self.assertTrue(isinstance(v, six.integer_types), 'should be integer, not {0}'.format(v))
            self.assertTrue(v >= 22 and v <= 33, 'should be more than 22 and less than 33, not {0}'.format(v))

    def test_array_with_object(self):
        """ array with object """
        a = self.rnd.render(
            self.app.resolve('#/definitions/array.object'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(a, list), 'should be a list, not {0}'.format(a))
        self.assertTrue(len(a) >=10 and len(a) <=40, 'length should be more than 10 and less than 40')
        for v in a:
            self.assertTrue(isinstance(v, dict), 'should be a dict, not {0}'.format(v))
            if 'id' in v:
                self.assertTrue(v['id'] >=50 and v['id'] <=100, 'should be between (50, 100), not {0}'.format(v['id']))
            if 'name' in v:
                self.assertTrue(isinstance(v['name'], six.string_types), 'should be string, not {0}'.format(v['name']))


class ObjectTestCase(unittest.TestCase):
    """ render 'object' (Model) types """
    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'object')
        ))
        kls.rnd = Renderer()

    def test_required(self):
        """ make sure minimal_property works """
        opt = self.rnd.default()
        opt['minimal_property'] = True
        for _ in six.moves.xrange(50):
            o = self.rnd.render(
                self.app.resolve('#/definitions/user'),
                opt=opt
            )
            self.assertTrue(isinstance(o, dict), 'should be a dict, not {0}'.format(o))
            self.assertTrue('id' in o, 'id is in required list')
            self.assertTrue('name' in o, 'name is in required list')
            self.assertTrue('email' not in o, 'email is not in required list, and it\'s minimal')

        opt['minimal_property'] = False
        yes = no = 0
        for _ in six.moves.xrange(50):
            o = self.rnd.render(
                self.app.resolve('#/definitions/user'),
                opt=opt
            )
            self.assertTrue(isinstance(o, dict), 'should be a dict, not {0}'.format(o))
            self.assertTrue('id' in o, 'id is in required list')
            self.assertTrue('name' in o, 'name is in required list')
            if 'email' in o:
                yes = yes + 1
            else:
                no = no + 1
        self.assertTrue(yes > 0 and no > 0, 'email should exist sometimes, Y{0}-N{1}'.format(yes, no))

    def test_additionalProperties(self):
        """ test additionalProperties """
        opt = self.rnd.default()
        opt['minimal_property'] = True
        for _ in six.moves.xrange(50):
            o = self.rnd.render(
                self.app.resolve('#/definitions/object.addp'),
                opt=opt
            )
            self.assertTrue(isinstance(o, dict), 'should be a dict, not {0}'.format(o))
            self.assertTrue(len(o) >= 20 and len(o) <= 50, 'should be between (20, 50), not {0}'.format(len(o)))
            for k, v in six.iteritems(o):
                self.assertTrue(isinstance(v, dict), 'should be a dict, not {0}'.format(v))
                self.assertTrue('id' in v, 'id is in required list')
                self.assertTrue('name' in v, 'name is in required list')
                self.assertTrue('email' not in v, 'email is not in required list, and it\'s minimal')

    def test_template(self):
        """ make sure object_template works """
        id_ = uuid.uuid4()
        opt = self.rnd.default()
        opt['object_template'].update({
            'id': id_,
            'name': 'test-user'
        })
        obj = self.app.resolve('#/definitions/comment')
        for _ in six.moves.xrange(50):
            o = self.rnd.render(
                obj,
                opt=opt
            )
            self.assertEqual(o['id'], id_)
            self.assertEqual(o['name'], 'test-user')
            self.assertTrue(validate_email(o['comment']))
            self.assertTrue(isinstance(o['time'], datetime.datetime), 'should be a datetime, not {0}'.format(str(type(o['time']))))

    def test_max_property(self):
        """ make sure max_property works """
        opt = self.rnd.default()
        opt['max_property'] = True
        obj = self.app.resolve('#/definitions/user2')
        for _ in six.moves.xrange(50):
            o = self.rnd.render(
                obj,
                opt=opt
            )
            self.assertTrue('id' in o, 'should have id')
            self.assertTrue('name' in o, 'should have name')
            self.assertTrue('email' in o, 'should have email')


class ParameterTestCase(unittest.TestCase):
    """ test case for rendering a single Parameter,
    type/format specific tests are covered by other
    test cases.
    """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'parameter')
        ))
        kls.rnd = Renderer()

    def test_header(self):
        v = self.rnd.render(
            self.app.resolve('#/parameters/header.string'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(v, six.string_types), 'should be string, not {0}'.format(str(type(v))))

    def test_path(self):
        v = self.rnd.render(
            self.app.resolve('#/parameters/path.string'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(v, six.string_types), 'should be string, not {0}'.format(str(type(v))))

    def test_query(self):
        v = self.rnd.render(
            self.app.resolve('#/parameters/query.string'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(v, six.string_types), 'should be string, not {0}'.format(str(type(v))))

    def test_body(self):
        v = self.rnd.render(
            self.app.resolve('#/parameters/body.string'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(v, six.string_types), 'should be string, not {0}'.format(str(type(v))))

    def test_form(self):
        v = self.rnd.render(
            self.app.resolve('#/parameters/form.string'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(v, six.string_types), 'should be string, not {0}'.format(str(type(v))))

    def test_file(self):
        v = self.rnd.render(
            self.app.resolve('#/parameters/form.file'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(v, dict), 'should be a dict, not {0}'.format(str(type(v))))
        self.assertEqual(v['header']['Content-Type'], 'text/plain')
        self.assertEqual(v['header']['Content-Transfer-Encoding'], 'binary')
        self.assertEqual(v['filename'], '')
        self.assertTrue(hasattr(v['data'].read, '__call__'), 'should have a read function')

        # register several file objects
        p = [get_test_data_folder(
            version='2.0',
            which=path.join('render', 'parameter')
        ), get_test_data_folder(
            version='2.0',
            which=path.join('render', 'other')
        ), get_test_data_folder(
            version='2.0',
            which=path.join('render', 'object')
        )]
        opt = self.rnd.default()
        for pp in p:
            opt['files'].append(dict(
            header={},
            filename=pp,
            data=None
        ))
        for _ in six.moves.xrange(50):
            v = self.rnd.render(
                self.app.resolve('#/parameters/form.file'),
                opt=opt
            )
            self.assertTrue(v['filename'] in p, 'filename should be registered, not {0}'.format(v['filename']))


class OperationTestCase(unittest.TestCase):
    """ test case for rendering an Operation """
    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'operation')
        ))
        kls.rnd = Renderer()

    def test_set_1(self):
        """ test query, header, path parameter """
        op = self.app.s("api.1/{path_email}").get
        ps = self.rnd.render_all(op)

        # checking generated parameter set
        self.assertTrue(isinstance(ps, dict), 'should be a dict, not {0}'.format(ps))
        self.assertTrue("path_email" in ps, 'path_email should be in set, but {0}'.format(ps))
        self.assertTrue(isinstance(ps['path_email'], six.string_types), 'should be string, not {0}'.format(str(type(ps['path_email']))))
        self.assertTrue(validate_email(ps['path_email']), 'should be a valid email, not {0}'.format(ps['path_email']))
        self.assertTrue("header.uuid" in ps, 'header.uuid should be in set, but {0}'.format(ps))
        self.assertTrue(isinstance(ps['header.uuid'], uuid.UUID), 'should be an uuid.UUID, not {0}'.format(str(type(ps['header.uuid']))))
        self.assertTrue("query.integer" in ps, 'query.integer should be in set, but {0}'.format(ps))
        self.assertTrue(isinstance(ps['query.integer'], six.integer_types), 'should be int, not {0}'.format(str(type(ps['query.integer']))))

        # ok to be passed into Operation object
        req, resp = op(**ps)
        req.prepare(scheme='http', handle_files=False)

        # query
        found_query = False
        for v in req.query:
            if v[0] == 'query.integer':
                found_query = True
                break
        self.assertEqual(found_query, True)

        # header
        found_header = False
        for k, v in six.iteritems(req.header):
            if k == 'header.uuid':
                found_header = True
                break
        self.assertEqual(found_header, True)

        # path
        self.assertTrue(validate_email(six.moves.urllib.parse.unquote_plus(req.path[len('/api.1/'):])), 'should contain a valid email, not {0}'.format(req.path))

    def test_body(self):
        """ test body parameter """
        op = self.app.s('api.1').post
        ps = self.rnd.render_all(op)

        self.assertTrue(isinstance(ps, dict), 'should be a dict, not {0}'.format(str(type(ps))))
        self.assertTrue('body.object' in ps, 'should contain body.object, not {0}'.format(ps))
        self.assertTrue(isinstance(ps['body.object'], dict), 'should be dict, not {0}'.format(str(type(ps['body.object']))))

        req, resp = op(**ps)
        req.prepare(scheme='http', handle_files=False)

        # body
        v = json.loads(req.data)
        self.assertTrue(validate_email(v['contact']), 'should have a valid email in contact, not {0}'.format(v))
        self.assertTrue(isinstance(v['name'], six.string_types), 'should have a string in name, not {0}'.format(v))
        self.assertTrue(isinstance(v['id'], six.integer_types), 'should have a int in id, not {0}'.format(v))

    def test_form(self):
        """ test form (urlencode) """
        op = self.app.s('api.1').put
        ps = self.rnd.render_all(op)

        self.assertTrue(isinstance(ps, dict), 'should be a dict, not {0}'.format(str(type(ps))))
        self.assertTrue('form.email' in ps, 'should contain body.object, not {0}'.format(ps))
        self.assertTrue(validate_email(ps['form.email']), 'should be valid email, not {0}'.format(ps['form.email']))

        req, resp = op(**ps)
        req.prepare(scheme='http', handle_files=False)

        # form(urlencode)
        self.assertEqual(req.data, six.moves.urllib.parse.urlencode(ps))

    def test_file(self):
        """ test form (file) """
        op = self.app.s('api.2').post
        ps = self.rnd.render_all(op)

        self.assertTrue(hasattr(ps['thumbnail']['data'].read, '__call__'), '\'data\' should be readable')

        req, resp = op(**ps)
        req.prepare(scheme='http', handle_files=False)

        # file
        self.assertTrue(isinstance(req.files['thumbnail'], File), 'should be a File, not {0}'.format(req.files))

    def test_template(self):
        """ make sure template works """
        op = self.app.s("api.1/{path_email}").get
        opt = self.rnd.default()
        opt['parameter_template'].update({
            'path_email': 'a123@b.com'
        })
        for _ in six.moves.xrange(50):
            ps = self.rnd.render_all(op, opt=opt)
            self.assertEqual(ps['path_email'], 'a123@b.com')

        # test object in body
        opt['object_template'].update({
            'name': 'user123'
        })
        op = self.app.s('api.1').post
        for _ in six.moves.xrange(50):
            ps = self.rnd.render_all(op, opt=opt)
            self.assertEqual(ps['body.object']['name'], 'user123')

    def test_minimal(self):
        """ make sure minimal_parameter works """
        op = self.app.s('api.1').get
        opt = self.rnd.default()
        opt['minimal_parameter'] = True
        for _ in six.moves.xrange(50):
            ps = self.rnd.render_all(op, opt=opt)
            self.assertTrue('p1' not in ps, 'p1 should not existed')
            self.assertTrue('p2' in ps, 'p2 should exist')
            self.assertTrue('p3' in ps, 'p3 should exist')

        opt['minimal_parameter'] = False
        count = 0
        for _ in six.moves.xrange(50):
            ps = self.rnd.render_all(op, opt=opt)
            if 'p1' in ps:
                count = count + 1
            self.assertTrue('p2' in ps, 'p2 should exist')
            self.assertTrue('p3' in ps, 'p3 should exist')
        self.assertTrue(count > 0, 'count should be larger than zero, not {0}'.format(count))

    def test_max_parameter(self):
        """ make sure max_parameter works """
        op = self.app.s('api.2').get
        opt = self.rnd.default()
        opt['max_parameter'] = True
        for _ in six.moves.xrange(50):
            ps = self.rnd.render_all(op, opt=opt)
            self.assertTrue('p1' in ps, 'p1 should exists')
            self.assertTrue('p2' in ps, 'p2 should exists')
            self.assertTrue('p2' in ps, 'p3 should exists')

    def test_exclude(self):
        """ make sure exclude works """
        op = self.app.s('api.1').get
        opt = self.rnd.default()
        opt['minimal_parameter'] = False
        for _ in six.moves.xrange(50):
            ps = self.rnd.render_all(op, exclude=['p1'], opt=opt)
            self.assertTrue('p1' not in ps, 'p1 should be excluded')
