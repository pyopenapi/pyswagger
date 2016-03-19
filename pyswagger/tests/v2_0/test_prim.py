from pyswagger import SwaggerApp, primitives, errs, io
from ..utils import get_test_data_folder
from pyswagger.spec.v2_0 import objects, parser
from pyswagger.spec import base
from pyswagger.utils import jp_compose
from pyswagger.primitives import SwaggerPrimitive
import os
import unittest
import datetime
import six


class SchemaTestCase(unittest.TestCase):
    """ test for Schema object """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='2.0', which=os.path.join('schema', 'model')))

    def test_model_tag(self):
        """ test basic model """
        t = self.app.resolve('#/definitions/Tag')
        self.assertTrue(isinstance(t, objects.Schema))

        v = t._prim_(dict(id=1, name='Hairy'), self.app.prim_factory)
        self.assertTrue(isinstance(v, primitives.Model))
        self.assertEqual(v.id, 1)
        self.assertEqual(v.name, 'Hairy')

    def test_model_pet(self):
        """ test complex model, including
        model inheritance
        """
        p = self.app.resolve('#/definitions/Pet')
        self.assertTrue(isinstance(p, objects.Schema))

        v = p._prim_(dict(
            name='Buf',
            photoUrls=['http://flickr.com', 'http://www.google.com'],
            id=10,
            category=dict(
                id=1,
                name='dog'
            ),
            tags=[
                dict(id=1, name='Hairy'),
                dict(id=2, name='south'),
            ]
        ), self.app.prim_factory)
        self.assertTrue(isinstance(v, primitives.Model))
        self.assertEqual(v.name, 'Buf')
        self.assertEqual(v.photoUrls[0], 'http://flickr.com')
        self.assertEqual(v.photoUrls[1], 'http://www.google.com')
        self.assertEqual(v.id, 10)
        self.assertTrue(isinstance(v.tags[0], primitives.Model))
        self.assertTrue(v.tags[0].id, 1)
        self.assertTrue(v.tags[0].name, 'Hairy')
        self.assertTrue(isinstance(v.category, primitives.Model))
        self.assertTrue(v.category.id, 1)
        self.assertTrue(v.category.name, 'dog')

    def test_model_employee(self):
        """ test model with allOf only
        """
        e = self.app.resolve("#/definitions/Employee")
        self.assertTrue(isinstance(e, objects.Schema))

        v = e._prim_(dict(
            id=1,
            skill_id=2,
            location="home",
            skill_name="coding",
            email="a@a.com"
        ), self.app.prim_factory)
        self.assertTrue(isinstance(v, primitives.Model))
        self.assertEqual(v.id, 1)
        self.assertEqual(v.skill_id, 2)
        self.assertEqual(v.location, "home")
        self.assertEqual(v.skill_name, "coding")

        self.assertRaises(
            errs.ValidationError,
            e._prim_, dict(
                id=1,
                skill_id=2,
                location="home",
                skill_name="coding",
                email="a..a@a.com"
            ), self.app.prim_factory
        )

    def test_model_boss(self):
        """ test model with allOf and properties
        """
        b = self.app.resolve("#/definitions/Boss")
        self.assertTrue(isinstance(b, objects.Schema))

        v = b._prim_(dict(
            id=1,
            location="office",
            boss_name="not you"
        ), self.app.prim_factory)
        self.assertTrue(isinstance(v, primitives.Model))
        self.assertEqual(v.id, 1)
        self.assertEqual(v.location, "office")
        self.assertEqual(v.boss_name, "not you")

    def test_int(self):
        """ test integer,
        schema is separated into parts
        """
        i = self.app.resolve("#/definitions/int")

        self.assertRaises(errs.ValidationError, i._prim_, 200, self.app.prim_factory)
        self.assertRaises(errs.ValidationError, i._prim_, 99, self.app.prim_factory)

    def test_array_of_int(self):
        """ test array of integer """
        i = self.app.resolve('#/definitions/array_int')

        # pass
        i._prim_([1, 1, 1, 1, 1], self.app.prim_factory)
        i._prim_([1, 1], self.app.prim_factory)

        # failed
        self.assertRaises(errs.ValidationError, i._prim_, [1, 1, 1, 1, 1, 1], self.app.prim_factory)
        self.assertRaises(errs.ValidationError, i._prim_, [1], self.app.prim_factory)


    def test_num_multiple_of(self):
        """ test multipleOf """
        i = self.app.resolve("#/definitions/num_multipleOf")

        self.assertRaises(errs.ValidationError, i._prim_, 4, self.app.prim_factory)
        i._prim_(5, self.app.prim_factory) # should raise nothing

    def test_str_enum(self):
        """ test str enum """
        e = self.app.resolve("#/definitions/str_enum")

        self.assertRaises(errs.ValidationError, e._prim_, "yellow", self.app.prim_factory)
        e._prim_("green", self.app.prim_factory) # should raise nothing

    def test_byte(self):
        """ test byte """
        b = self.app.resolve("#/definitions/byte")

        bv = b._prim_("BBBBB", self.app.prim_factory)
        self.assertEqual(str(bv), "BBBBB", self.app.prim_factory)
        self.assertEqual(bv.to_json(), six.b("QkJCQkI="))

    def test_date(self):
        """ test date """
        d = self.app.resolve("#/definitions/date")

        # test input of constructor
        self.assertEqual(str(d._prim_(float(0), self.app.prim_factory)), "1970-01-01")
        self.assertEqual(str(d._prim_(datetime.date.fromtimestamp(0), self.app.prim_factory)), "1970-01-01")
        self.assertEqual(str(d._prim_(datetime.date.fromtimestamp(0).isoformat(), self.app.prim_factory)), "1970-01-01")

        # to_json
        dv = d._prim_(float(0), self.app.prim_factory)
        self.assertEqual(dv.to_json(), "1970-01-01")

    def test_date_time(self):
        """ test date-time """
        d = self.app.resolve("#/definitions/date-time")

        # test input of constructor
        self.assertEqual(str(d._prim_(float(0), self.app.prim_factory)), "1970-01-01T00:00:00")
        self.assertEqual(str(d._prim_(datetime.datetime.utcfromtimestamp(0), self.app.prim_factory)), "1970-01-01T00:00:00")
        self.assertEqual(str(d._prim_(datetime.datetime.utcfromtimestamp(0).isoformat(), self.app.prim_factory)), "1970-01-01T00:00:00")

        # to_json
        dv = d._prim_(float(0), self.app.prim_factory)
        self.assertEqual(dv.to_json(), "1970-01-01T00:00:00")

    def test_model_bool(self):
        """ test a model containing boolean """
        d = self.app.resolve("#/definitions/model_bool")

        dv = d._prim_(dict(bool_val=True), self.app.prim_factory) 
        # try to access it
        self.assertEqual(dv.bool_val, True)

    def test_email(self):
        """ test string in email format """
        d = self.app.resolve('#/definitions/email')

        dv = d._prim_('a@a.com', self.app.prim_factory)
        self.assertEqual(dv, 'a@a.com')
        self.assertRaises(errs.ValidationError, d._prim_, 'a@a..com', self.app.prim_factory)

    def test_uuid(self):
        """ test string in uuid format """
        d = self.app.resolve('#/definitions/uuid')

        # string
        dv = d._prim_('12345678-1234-5678-1234-567812345678', self.app.prim_factory)
        self.assertTrue(isinstance(dv, primitives.UUID), 'should be an primitives.UUID, not {0}'.format(str(type(dv))))
        self.assertEqual(str(dv), '12345678-1234-5678-1234-567812345678')

        # byte
        dv = d._prim_(six.b('\x78\x56\x34\x12\x34\x12\x78\x56\x12\x34\x56\x78\x12\x34\x56\x78'), self.app.prim_factory)
        self.assertTrue(isinstance(dv, primitives.UUID), 'should be an primitives.UUID, not {0}'.format(dv))
        self.assertEqual(dv.v.bytes, six.b('\x78\x56\x34\x12\x34\x12\x78\x56\x12\x34\x56\x78\x12\x34\x56\x78'))


class HeaderTestCase(unittest.TestCase):
    """ test for Header object """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='2.0', which=os.path.join('schema', 'model')))

    def test_simple_array(self):
        """ header in array """
        p1 = self.app.resolve(jp_compose(['#', 'paths', '/t', 'get', 'parameters', '0']))
        self.assertTrue(isinstance(p1, objects.Parameter))

        v = p1._prim_([1, 2, 3, 4, 5], self.app.prim_factory)
        self.assertTrue(isinstance(v, primitives.Array))
        self.assertEqual(str(v), '1,2,3,4,5')

    def test_integer_limit(self):
        """ header in integer """
        p2 = self.app.resolve(jp_compose(['#', 'paths', '/t', 'get', 'parameters', '1']))
        self.assertTrue(isinstance(p2, objects.Parameter))

        self.assertRaises(errs.ValidationError, p2._prim_, 101, self.app.prim_factory)
        self.assertRaises(errs.ValidationError, p2._prim_, -1, self.app.prim_factory)

    def test_multi_level_array(self):
        """ header in array of array """
        p3 = self.app.resolve(jp_compose(['#', 'paths', '/t', 'get', 'parameters', '2']))
        self.assertTrue(isinstance(p3, objects.Parameter))

        self.assertEqual(str(p3._prim_(
            [
                [
                    [1,2],
                    [3,4],
                    [5,6]
                ],
                [
                    [7,8],
                    [9,10]
                ],
                [
                    [11,12],
                    [13,14]
                ]
            ], self.app.prim_factory)), '1|2,3|4,5|6 7|8,9|10 11|12,13|14')

    def test_header_in_response(self):
        """ header in response """
        resp = io.SwaggerResponse(self.app.s('/t').get)

        resp.apply_with(status=200, raw=None, header=dict(
            test='1|2,3|4,5|6 7|8,9|10 11|12,13|14'
        ))
        # note that the test case here is the same as the one above,
        # difference is we would wrap an additional array in header
        self.assertEqual(resp.header['test'], [[
            [
                [1,2],
                [3,4],
                [5,6]
            ],
            [
                [7,8],
                [9,10]
            ],
            [
                [11,12],
                [13,14]
            ]
        ]])


class AdditionalPropertiesTestCase(unittest.TestCase):
    """ test case for additionalProperties """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='2.0', which=os.path.join('schema', 'additionalProperties')))

    def test_merge(self):
        """ verify merge along with additionalProperties """
        # Schema
        addp = self.app.resolve('#/definitions/add_prop')
        final = objects.Schema(base.NullContext())
        final.merge(addp, parser.SchemaContext)

        # True
        addp = self.app.resolve('#/definitions/add_prop_bool')
        final = objects.Schema(base.NullContext())
        final.merge(addp, parser.SchemaContext)

        # False
        addp = self.app.resolve('#/definitions/add_prop_false')
        final = objects.Schema(base.NullContext())
        final.merge(addp, parser.SchemaContext)

        # nested with allOf
        addp = self.app.resolve('#/definitions/add_prop_nested')
        final = objects.Schema(base.NullContext())
        final.merge(addp, parser.SchemaContext)

    def test_with_schema(self):
        m = self.app.prim_factory.produce(
            self.app.resolve('#/definitions/add_prop'),
            dict(
                name_of_map='test',
                category1=dict(
                    id=1,
                    name='cat'
                ),
                category2=dict(
                    id=2,
                    name='dog'
                ),
                category3=dict(
                    id=3,
                    name='fish'
                )
            ))

        self.assertTrue(isinstance(m, primitives.Model))
        self.assertEqual(m.name_of_map, 'test')
        self.assertEqual(m.category1.id, 1)
        self.assertEqual(m.category1.name, 'cat')
        self.assertEqual(m.category2.id, 2)
        self.assertEqual(m.category2.name, 'dog')
        self.assertEqual(m.category3.id, 3)
        self.assertEqual(m.category3.name, 'fish')

    def test_with_bool(self):
        d = self.app.resolve('#/definitions/add_prop_bool')
        m = self.app.prim_factory.produce(
            d,
            dict(
                name='test_bool',
                category1=1,
                category2='test_qoo'
            )
        )

        self.assertTrue(isinstance(m, primitives.Model))
        self.assertEqual(m.name, 'test_bool')
        self.assertEqual(m.category1, 1)
        self.assertEqual(m.category2, 'test_qoo')

    def test_with_bool_false(self):
        d = self.app.resolve('#/definitions/add_prop_false')
        m = self.app.prim_factory.produce(
            d,
            dict(
                name='test_bool',
                category1=1,
                category2='test_qoo'
            )
        )

        self.assertTrue(isinstance(m, primitives.Model))
        self.assertEqual(m.name, 'test_bool')
        self.assertTrue('category1' not in m)
        self.assertTrue('category2' not in m)

    def test_with_allof_limitation(self):
        """ additionalProperties would accept all keys,
        we need to make sure nested model process those keys before
        additionalProperties intecept all keys
        """
        d = self.app.resolve('#/definitions/add_prop_nested')
        self.assertRaises(errs.ValidationError, self.app.prim_factory.produce,
            d,
            dict(
                my_int=99
            )
        )

    def test_array_addp_without_prop(self):
        """ special case for array of items with additionalProperties
        and without properties
        """
        d = self.app.resolve('#/definitions/addp_no_prop')
        m = self.app.prim_factory.produce(
            d, [
                dict(a=1, b=2, c=3),
                dict(name='john', email='xx@gmail.com'),
            ]
        )
        self.assertEqual(len(m), 2)
        self.assertEqual(m[0], dict(a=1, b=2, c=3)) # although we didn't validate it, we should still output it.
        self.assertEqual(m[1], dict(name='john', email='xx@gmail.com'))


class ParameterTestCase(unittest.TestCase):
    """ test for Parameter object """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='2.0', which=os.path.join('schema', 'model')))

    def test_unknown(self):
        p = self.app.resolve('#/paths/~1t/put')
        self.assertRaises(ValueError, p, p1='tom', p2='mary', p3='qoo', p4='unknown') 


class PrimitiveExtensionTestCase(unittest.TestCase):
    """ test for extending primitives """

    @classmethod
    def setUpClass(kls):
        factory = SwaggerPrimitive()
        def decode_int(obj, val, ctx):
            # minus 1
            return int(val) - 1

        def decode_str(obj, val, ctx):
            # remove the last char
            return str(val)[:-1]

        def str_no_validate(obj, val, ctx):
            # same as the one used in pyswagger, but no validation
            return str(val)

        factory.register('encoded_integer', None, decode_int)
        factory.register('string', 'special_encoded', decode_str)
        factory.register('string', None, str_no_validate, _2nd_pass=None)

        kls.app = SwaggerApp.load(get_test_data_folder(
            version='2.0',
            which=os.path.join('schema', 'extension'),
        ), prim=factory)
        kls.app.prepare()

    def test_extend(self):
        """ extend primitives with user defined type/format handler """
        m1 = self.app.resolve('#/definitions/m1')
        v = m1._prim_({
            "_id": 100,
            "name": 'Ms',
        }, self.app.prim_factory)
        self.assertEqual(v._id, 99)
        self.assertEqual(v.name, 'M')

    def test_overwrite(self):
        """ overrite type/format handler used in pyswagger """
        m1 = self.app.resolve('#/definitions/m1')
        v = m1._prim_({
            "job":"man"
        }, self.app.prim_factory)
        # should not raise
        self.assertEqual(v.job, "man")

        app = SwaggerApp.create(get_test_data_folder(
            version='2.0',
            which=os.path.join('schema', 'extension')
        ))
        m1 = app.resolve('#/definitions/m1')
        self.assertRaises(errs.ValidationError, m1._prim_, {'job':'man'}, app.prim_factory)
        # should raise
