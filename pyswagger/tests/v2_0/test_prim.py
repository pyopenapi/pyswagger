from pyswagger import SwaggerApp, primitives, errs
from ..utils import get_test_data_folder
from pyswagger.spec.v2_0 import objects
from pyswagger.utils import jp_compose
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

        v = t._prim_(dict(id=1, name='Hairy'))
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
        ))
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
            skill_name="coding"
        ))
        self.assertTrue(isinstance(v, primitives.Model))
        self.assertEqual(v.id, 1)
        self.assertEqual(v.skill_id, 2)
        self.assertEqual(v.location, "home")
        self.assertEqual(v.skill_name, "coding")

    def test_model_boss(self):
        """ test model with allOf and properties
        """
        b = self.app.resolve("#/definitions/Boss")
        self.assertTrue(isinstance(b, objects.Schema))

        v = b._prim_(dict(
            id=1,
            location="office",
            boss_name="not you"
        ))
        self.assertTrue(isinstance(v, primitives.Model))
        self.assertEqual(v.id, 1)
        self.assertEqual(v.location, "office")
        self.assertEqual(v.boss_name, "not you")

    def test_int(self):
        """ test integer,
        schema is separated into parts
        """
        i = self.app.resolve("#/definitions/int")

        self.assertRaises(errs.ValidationError, i._prim_, 200)
        self.assertRaises(errs.ValidationError, i._prim_, 99)

    def test_array_of_int(self):
        """ test array of integer """
        i = self.app.resolve('#/definitions/array_int')

        # pass
        i._prim_([1, 1, 1, 1, 1])
        i._prim_([1, 1])

        # failed
        self.assertRaises(errs.ValidationError, i._prim_, [1, 1, 1, 1, 1, 1])
        self.assertRaises(errs.ValidationError, i._prim_, [1])


    def test_num_multiple_of(self):
        """ test multipleOf """
        i = self.app.resolve("#/definitions/num_multipleOf")

        self.assertRaises(errs.ValidationError, i._prim_, 4)
        i._prim_(5) # should raise nothing

    def test_str_enum(self):
        """ test str enum """
        e = self.app.resolve("#/definitions/str_enum")

        self.assertRaises(errs.ValidationError, e._prim_, "yellow")
        e._prim_("green") # should raise nothing

    def test_byte(self):
        """ test byte """
        b = self.app.resolve("#/definitions/byte")

        bv = b._prim_("BBBBB")
        self.assertEqual(str(bv), "BBBBB")
        self.assertEqual(bv.to_json(), six.b("QkJCQkI="))

    def test_date(self):
        """ test date """
        d = self.app.resolve("#/definitions/date")

        # test input of constructor
        self.assertEqual(str(d._prim_(float(0))), "1970-01-01")
        self.assertEqual(str(d._prim_(datetime.date.fromtimestamp(0))), "1970-01-01")
        self.assertEqual(str(d._prim_(datetime.date.fromtimestamp(0).isoformat())), "1970-01-01")

        # to_json
        dv = d._prim_(float(0))
        self.assertEqual(dv.to_json(), "1970-01-01")

    def test_date_time(self):
        """ test date-time """
        d = self.app.resolve("#/definitions/date-time")

        # test input of constructor
        self.assertEqual(str(d._prim_(float(0))), "1970-01-01T00:00:00")
        self.assertEqual(str(d._prim_(datetime.datetime.utcfromtimestamp(0))), "1970-01-01T00:00:00")
        self.assertEqual(str(d._prim_(datetime.datetime.utcfromtimestamp(0).isoformat())), "1970-01-01T00:00:00")

        # to_json
        dv = d._prim_(float(0))
        self.assertEqual(dv.to_json(), "1970-01-01T00:00:00")

    def test_model_bool(self):
        """ test a model containing boolean """
        d = self.app.resolve("#/definitions/model_bool")

        dv = d._prim_(dict(bool_val=True)) 
        # try to access it
        self.assertEqual(dv.bool_val, True)

class HeaderTestCase(unittest.TestCase):
    """ test for Header object """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='2.0', which=os.path.join('schema', 'model')))

    def test_simple_array(self):
        """ header in array """
        p1 = self.app.resolve(jp_compose(['#', 'paths', '/t', 'get', 'parameters', '0']))
        self.assertTrue(isinstance(p1, objects.Parameter))

        v = p1._prim_([1, 2, 3, 4, 5])
        self.assertTrue(isinstance(v, primitives.Array))
        self.assertEqual(str(v), '1,2,3,4,5')

    def test_integer_limit(self):
        """ header in integer """
        p2 = self.app.resolve(jp_compose(['#', 'paths', '/t', 'get', 'parameters', '1']))
        self.assertTrue(isinstance(p2, objects.Parameter))

        self.assertRaises(errs.ValidationError, p2._prim_, 101)
        self.assertRaises(errs.ValidationError, p2._prim_, -1)

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
            ]
        )), '1|2,3|4,5|6 7|8,9|10 11|12,13|14')


class AdditionalPropertiesTestCase(unittest.TestCase):
    """ test case for additionalProperties """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='2.0', which=os.path.join('schema', 'additionalProperties')))

    def test_with_schema(self):
        m = primitives.prim_factory(
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
        m = primitives.prim_factory(
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
        m = primitives.prim_factory(
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
        self.assertRaises(errs.ValidationError, primitives.prim_factory,
            d,
            dict(
                my_int=99
            )
        )


class ParameterTestCase(unittest.TestCase):
    """ test for Parameter object """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='2.0', which=os.path.join('schema', 'model')))

    def test_unknown(self):
        p = self.app.resolve('#/paths/~1t/put')
        self.assertRaises(ValueError, p, p1='tom', p2='mary', p3='qoo', p4='unknown') 

