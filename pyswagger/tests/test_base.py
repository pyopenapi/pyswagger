from __future__ import absolute_import
from pyswagger import base
import unittest
import weakref
import six


class ChildObj(six.with_metaclass(base.FieldMeta, base.BaseObj)):
    pass

class ChildContext(base.Context):
    __swagger_ref_object__ = ChildObj

class TestObj(six.with_metaclass(base.FieldMeta, base.BaseObj)):
    __swagger_fields__ = [
        ('a', []),
        ('b', {}),
        ('c', {}),
        ('d', None),
        ('f', None)
    ]

class TestContext(base.Context):
    __swagger_ref_object__ = TestObj
    __swagger_child__ = [
        ('a', base.ContainerType.list_, ChildContext),
        ('b', base.ContainerType.dict_, ChildContext),
        ('c', base.ContainerType.dict_of_list_, ChildContext),
        ('d', None, ChildContext),
    ]

class SwaggerBaseTestCase(unittest.TestCase):
    """ test things in base.py """

    def test_baseobj_children(self):
        """ test _children_ """
        tmp = {'t': {}}
        obj = {'a': [{}, {}, {}], 'b': {'/a': {}, '~b': {}, 'cc': {}}}
        with TestContext(tmp, 't') as ctx:
            ctx.parse(obj)
        c = tmp['t']._children_.keys()

        self.assertEqual(sorted(c), sorted(['a/0', 'a/1', 'a/2', 'b/cc', 'b/~0b', 'b/~1a']))

    def test_baseobj_parent(self):
        """ test _parent_ """
        tmp = {'t': {}}
        obj = {'a': [{}], 'b': {'bb': {}}, 'c': {'cc': [{}]}, 'd': {}}
        with TestContext(tmp, 't') as ctx:
            ctx.parse(obj)

        def _check(o):
            self.assertTrue(isinstance(o, ChildObj))
            self.assertEqual(id(tmp['t']), id(o._parent_))

        _check(tmp['t'].a[0])
        _check(tmp['t'].b['bb'])
        _check(tmp['t'].c['cc'][0])
        _check(tmp['t'].d)

    def test_field_rename(self):
        """ renamed field name """

        class TestRenameObj(six.with_metaclass(base.FieldMeta, base.BaseObj)):
            __swagger_fields__ = [('a', None)]
            __swagger_rename__ = {'a': 'b'}
 
        class TestRenameContext(base.Context):
            __swagger_ref_object__ = TestRenameObj

        tmp = {'t': {}}
        obj = {'a': 1}
        with TestRenameContext(tmp, 't') as ctx:
            ctx.parse(obj)

        # make sure there is no 'a' property
        self.assertRaises(AttributeError, lambda x: x.a, tmp['t'])
        # make sure property 'b' exists
        self.assertTrue(tmp['t'].b, 1)

    def test_field_default_value(self):
        """ field default value, make sure we won't reference to a global declared list_
        """
        o1 = TestObj(base.NullContext())
        o2 = TestObj(base.NullContext())
        self.assertTrue(id(o1.a) != id(o2.a))

    def test_merge(self):
        """ test merge function """
        tmp = {'t': {}}
        obj1 = {'a': [{}, {}, {}], 'd': {}, 'f': ''}
        obj2 = {'a': [{}]}

        with TestContext(tmp, 't') as ctx:
            ctx.parse(obj1)
        o1 = tmp['t']

        with TestContext(tmp, 't') as ctx:
            ctx.parse(obj2)
        o2 = tmp['t']

        self.assertTrue(len(o2.a), 1)
        self.assertEqual(o2.d, None)

        o2.merge(o1)
        self.assertTrue(len(o2.a), 1)
        self.assertEqaul(o2.f, '')
        self.assertTrue(isinstance(o2.d, ChildObj))
        self.assertTrue(isinstance(o2.d, weakref.ProxyTypes))

