from __future__ import absolute_import
from pyswagger import base
import unittest
import six


class SwaggerBaseTestCase(unittest.TestCase):
    """ test things in base.py """

    def test_baseobj_children(self):
        """ test _children_ """
        class ChildObj(six.with_metaclass(base.FieldMeta, base.BaseObj)):
            pass

        class ChildContext(base.Context):
            __swagger_ref_object__ = ChildObj

        class TestObj(six.with_metaclass(base.FieldMeta, base.BaseObj)):
            __swagger_fields__ = [
                ('a', []),
                ('b', {}),
            ]

        class TestContext(base.Context):
            __swagger_ref_object__ = TestObj
            __swagger_child__ = [
                ('a', base.ContainerType.list_, ChildContext),
                ('b', base.ContainerType.dict_, ChildContext),
            ]

        tmp = {'t': {}}
        obj = {'a': [{}, {}, {}], 'b': {'/a': {}, '~b': {}, 'cc': {}}}
        with TestContext(tmp, 't') as ctx:
            ctx.parse(obj)
        c = [c[0] for c in tmp['t']._children_]

        self.assertEqual(c, ['a/0', 'a/1', 'a/2', 'b/cc', 'b/~0b', 'b/~1a'])

    def test_field_rename(self):
        """ renamed field name """

        class TestObj(six.with_metaclass(base.FieldMeta, base.BaseObj)):
            __swagger_fields__ = [('a', None)]
            __swagger_rename__ = {'a': 'b'}
 
        class TestContext(base.Context):
            __swagger_ref_object__ = TestObj

        tmp = {'t': {}}
        obj = {'a': 1}
        with TestContext(tmp, 't') as ctx:
            ctx.parse(obj)

        # make sure there is no 'a' property
        self.assertRaises(AttributeError, lambda x: x.a, tmp['t'])
        # make sure property 'b' exists
        self.assertTrue(tmp['t'].b, 1)

    def test_field_default_value(self):
        """ field default value """

        class TestObj(six.with_metaclass(base.FieldMeta, base.BaseObj)):
            __swagger_fields__ = [('a', [])]
 
        # make sure we won't reference to a global declared list
        o1 = TestObj(base.NullContext())
        o2 = TestObj(base.NullContext())
        self.assertTrue(id(o1.a) != id(o2.a))

