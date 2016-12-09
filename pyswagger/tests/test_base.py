from __future__ import absolute_import
from pyswagger.spec import base
import unittest
import six
import copy


class GrandChildObj(six.with_metaclass(base.FieldMeta, base.BaseObj)):
    __swagger_fields__ = {
        'name': ''
    }

class GrandChildContext(base.Context):
    __swagger_ref_object__ = GrandChildObj

class ChildObj(six.with_metaclass(base.FieldMeta, base.BaseObj)):
    __swagger_fields__ = {
        'g': None
    }

class ChildContext(base.Context):
    __swagger_ref_object__ = ChildObj
    __swagger_child__ = {
        'g': (None, GrandChildContext)
    }

class TObj(six.with_metaclass(base.FieldMeta, base.BaseObj)):
    __swagger_fields__ = {
        'a': [],
        'b': {},
        'c': {},
        'd': None,
        'f': None
    }

class TContext(base.Context):
    __swagger_ref_object__ = TObj
    __swagger_child__ = {
        'a': (base.ContainerType.list_, ChildContext),
        'b': (base.ContainerType.dict_, ChildContext),
        'c': (base.ContainerType.dict_of_list_, ChildContext),
        'd': (None, ChildContext),
    }

class SwaggerBaseTestCase(unittest.TestCase):
    """ test things in base.py """

    def test_baseobj_children(self):
        """ test _children_ """
        tmp = {'t': {}}
        obj = {'a': [{}, {}, {}], 'b': {'/a': {}, '~b': {}, 'cc': {}}}
        with TContext(tmp, 't') as ctx:
            ctx.parse(obj)
        c = tmp['t']._children_.keys()

        self.assertEqual(sorted(c), sorted(['a/0', 'a/1', 'a/2', 'b/cc', 'b/~0b', 'b/~1a']))

    def test_baseobj_parent(self):
        """ test _parent_ """
        tmp = {'t': {}}
        obj = {'a': [{}], 'b': {'bb': {}}, 'c': {'cc': [{}]}, 'd': {}}
        with TContext(tmp, 't') as ctx:
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
            __swagger_fields__ = {'a': None}
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
        o1 = TObj(base.NullContext())
        o2 = TObj(base.NullContext())
        self.assertTrue(id(o1.a) != id(o2.a))

    def test_merge(self):
        """ test merge function """

        class MergeObj(six.with_metaclass(base.FieldMeta, base.BaseObj)):
            __swagger_fields__ = {
                'ma': None,
                'mb': None,
                'mc': {},
                'md': {},
                'mf': [],
            }

        class MergeContext(base.Context):
            __swagger_child__ = {
                'ma': (None, TContext),
                'mb': (None, TContext),
                'mc': (base.ContainerType.dict_, TContext)
            }
            __swagger_ref_object__ = MergeObj


        tmp = {'t': {}}
        obj2 = {
            'mb':{'a':[{}, {}, {}]},
            'md':{'2': 2},
            'mf':[2, 3]
        }
        obj1 = {
            'ma':{'a':[{}, {}, {}, {}]},
            'mb':{'a':[{}, {}]},
            'mc':{'/a': {'a': [{}], 'b': {'bb': {}}, 'c': {'cc': [{}]}, 'd': {}}},
            'md':{'1': 1},
            'mf':[1, 2]
        }
        o3 = MergeObj(base.NullContext())

        with MergeContext(tmp, 't') as ctx:
            ctx.parse(obj1)
        o1 = tmp['t']

        with MergeContext(tmp, 't') as ctx:
            ctx.parse(obj2)
        o2 = tmp['t']

        def _chk(o_from, o_to):
            # existing children are not affected
            self.assertTrue(len(o_to.mb.a), 3)
            # non-existing children are fully copied3
            self.assertEqual(len(o_to.ma.a), 4)
            self.assertNotEqual(id(o_to.ma), id(o_from.ma))
            # make sure complex children are copied
            self.assertNotEqual(id(o_to.mc), id(o_from.mc))
            self.assertEqual(len(o_to.mc['/a'].a), 1)
            self.assertTrue(isinstance(o_to.mc['/a'].b['bb'], ChildObj))
            self.assertNotEqual(id(o_to.mc['/a'].b['bb']), id(o_from.mc['/a'].b['bb']))
            self.assertTrue(isinstance(o_to.mc['/a'].c['cc'][0], ChildObj))
            self.assertNotEqual(id(o_to.mc['/a'].c['cc'][0]), id(o_from.mc['/a'].c['cc'][0]))
            self.assertTrue(o_to.mc['/a'].d, ChildObj)
            self.assertNotEqual(id(o_to.mc['/a'].d), id(o1.mc['/a'].d))
            self.assertEqual(o_to.md, {'1': 1, '2': 2})
            self.assertEqual(sorted(o_to.mf), sorted([1, 2, 3]))

        def _chk_parent(o_from, o_to):
            for v in o_to.ma.a:
                self.assertEqual(id(v._parent_), id(o_to.ma))
                self.assertNotEqual(id(v._parent_), id(o_from.ma))

            self.assertEqual(id(o_to.ma._parent_), id(o_to))
            self.assertEqual(id(o_to.mb._parent_), id(o_to))
            self.assertEqual(id(o_to.mc['/a']._parent_), id(o_to))
            self.assertEqual(id(o_to.mc['/a'].a[0]._parent_), id(o_to.mc['/a']))
            self.assertEqual(id(o_to.mc['/a'].b['bb']._parent_), id(o_to.mc['/a']))
            self.assertEqual(id(o_to.mc['/a'].c['cc'][0]._parent_), id(o_to.mc['/a']))

        self.assertEqual(o2.ma, None)
        self.assertTrue(isinstance(o2.mb, TObj))
        self.assertTrue(len(o2.mb.a), 3)
        self.assertEqual(len(o2.mc), 0)

        id_mb = id(o2.mb)

        o2.merge(o1, MergeContext)
        self.assertNotEqual(id(o2.mb), id(o1.mb))
        self.assertEqual(id(o2.mb), id_mb)

        # cascade merge
        o3.merge(o2, MergeContext)

        _chk(o1, o2)
        _chk(o2, o3)
        _chk(o1, o3)

        _chk_parent(o1, o2)
        _chk_parent(o2, o3)
        _chk_parent(o1, o3)

    def test_merge_exclude(self):
        """ test 'exclude' in merge """
        tmp = {'t': {}}
        obj = {'a': [{}, {}, {}], 'b': {'/a': {}, '~b': {}, 'cc': {}}}
        with TContext(tmp, 't') as ctx:
            ctx.parse(obj)
        o = tmp['t']

        o1, o2 = TObj(base.NullContext()), TObj(base.NullContext())
        o1.merge(o, TContext)
        o2.merge(o, TContext, exclude=['b'])
        self.assertEqual(len(o1.a), 3)
        self.assertEqual(len(o2.a), 3)
        self.assertEqual(len(o1.b), 3)
        self.assertEqual(len(o2.b), 0)

    def test_resolve(self):
        """ test resolve function """
        tmp = {'t': {}}
        obj = {'a': [{}, {}, {}], 'b': {'/a': {}, '~b': {}, 'cc': {}}}
        with TContext(tmp, 't') as ctx:
            ctx.parse(obj)

        o = tmp['t']
        self.assertEqual(id(o.resolve('a')), id(o.a))
        self.assertEqual(id(o.resolve(['a'])), id(o.resolve('a')))
        self.assertEqual(id(o.resolve(['b', '/a'])), id(o.b['/a']))

    def test_is_produced(self):
        """ test is_produced function """
        class ChildNotOkContext(base.Context):
            __swagger_ref_object__ = ChildObj

            @classmethod
            def is_produced(kls, obj):
                return False

        class TestOkContext(base.Context):
            __swagger_ref_object__ = TObj
            __swagger_child__ = {
                'a': (None, ChildContext)
            }

        class TestNotOkContext(base.Context):
            __swagger_ref_object__ = TObj
            __swagger_child__ = {
                'a': (None, ChildNotOkContext)
            }

        tmp = {'t': {}}
        obj = {'a': {}}

        with TestOkContext(tmp, 't') as ctx:
            # should not raise
            ctx.parse(obj)

        ctx = TestNotOkContext(tmp, 't')
        try:
            # simulate what ContextManager does
            ctx.parse(obj)
            ctx.__exit__(None, None, None)
        except ValueError as e:
            self.failUnlessEqual(e.args, ('Object is not instance of ChildObj but ChildObj',))
        else:
            self.fail('ValueError not raised')

    def test_produce(self):
        """ test produce function """
        class TestBoolContext(base.Context):
            __swagger_ref_object__ = TObj
            __swagger_child__ = {
                'a': (None, ChildContext),
            }

            def produce(self):
                return True

        tmp = {'t': {}}
        obj = {'a': {}}
        with TestBoolContext(tmp, 't') as ctx:
            ctx.parse(obj)

        self.assertTrue(isinstance(tmp['t'], bool))
        self.assertEqual(tmp['t'], True)

    def test_compare(self):
        """ test compare """
        tmp = {'t': {}}
        obj = {
            'a': [{'g': {'name':'Tom'}}, {'g': {'name': 'Kevin'}}],
            'b': {
                'bb': {},
                'bbb': {'g': {'name': 'Owl'}}
            },
            'c': {
                'cc': [
                    {'g': {'name':'Mary'}}
                ]
            },
            'd': {}
        }
        with TContext(tmp, 't') as ctx:
            ctx.parse(obj)
        obj1 = tmp['t']

        # make sure ok when compare with self
        self.assertEqual((True, ''), obj1.compare(obj1))

        # make sure diff in list would be captured
        objt = copy.deepcopy(obj)
        objt['a'][0]['g']['name'] = 'Tom1'

        tmp = {'t': {}}
        with TContext(tmp, 't') as ctx:
            ctx.parse(objt)
        obj2 = tmp['t']
        self.assertEqual((False, 'a/0/g/name'), obj1.compare(obj2))

        # make sure re order in list would be ok
        objt = copy.deepcopy(obj)
        objt['a'][0], objt['a'][1] = objt['a'][1], objt['a'][0]

        tmp = {'t': {}}
        with TContext(tmp, 't') as ctx:
            ctx.parse(objt)
        obj3 = tmp['t']
        self.assertEqual((False, 'a/0/g/name'), obj1.compare(obj3))

        # make sure diff in dict would be captured
        objt = copy.deepcopy(obj)
        objt['b']['bbb']['g']['name'] = 'Leo'

        tmp = {'t': {}}
        with TContext(tmp, 't') as ctx:
            ctx.parse(objt)
        obj4 = tmp['t']
        self.assertEqual((False, 'b/bbb/g/name'), obj1.compare(obj4))

        # make sure diff in dict of list would be captured
        objt = copy.deepcopy(obj)
        objt['c']['cc'][0]['g']['name'] = 'Celios'

        tmp = {'t': {}}
        with TContext(tmp, 't') as ctx:
            ctx.parse(objt)
        obj5 = tmp['t']
        self.assertEqual((False, 'c/cc/0/g/name'), obj1.compare(obj5))

        # make sure diff in dict would be captured
        objt = copy.deepcopy(obj)
        objt['b']['bbbb'] = {'g': {'name': 'Leo'}}

        tmp = {'t': {}}
        with TContext(tmp, 't') as ctx:
            ctx.parse(objt)
        obj6 = tmp['t']
        self.assertEqual((False, 'b/bbbb'), obj1.compare(obj6))

    def test_inheritance(self):
        """ test case for multiple layers of inheritance of BaseObj
        """
        class A(six.with_metaclass(base.FieldMeta, base.BaseObj)):
            __swagger_fields__ = {'a': None}

        class B(six.with_metaclass(base.FieldMeta, A)):
            __swagger_fields__ = {'b': None}

        class C(six.with_metaclass(base.FieldMeta, B)):
            __swagger_fields__ = {'c': None}

        class D(six.with_metaclass(base.FieldMeta, C)):
            __swagger_fields__ = {'d': None}

        class Dx(base.Context):
            __swagger_ref_object__ = D

        obj = dict(a=1, b=2, c=3, d=4)
        tmp = {'t': {}}
        with Dx(tmp, 't') as ctx:
            ctx.parse(obj)

        d = tmp['t']
        self.assertEqual(d.a, 1)
        self.assertEqual(d.b, 2)
        self.assertEqual(d.c, 3)
        self.assertEqual(d.d, 4)

