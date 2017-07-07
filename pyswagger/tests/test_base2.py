from pyswagger.spec.base2 import (
    Base2, field, child,
    map_, list_,
    _Map, _List,
    )
import unittest


class BObj(Base2):
    __fields__ = {
        'bb': dict(builder=field),
    }

class AObj(Base2):
    __fields__ = {
        'a': dict(builder=field),
        'b': dict(builder=field, required=True),
        'c': dict(builder=child, child_builder=BObj),
    }

class CObj(Base2):
    __fields__ = {
        'cc': dict(builder=child, child_builder=map_(AObj)),
        'ccc': dict(builder=child, child_builder=list_(AObj)),
    }

class DObj(Base2):
    __fields__ = {
        'd1': dict(builder=child, child_builder=map_(list_(AObj))),
        'd2': dict(builder=child, child_builder=list_(map_(AObj))),
        'd3': dict(builder=child, child_builder=map_(map_(AObj))),
    }

def if_not_a(obj_class):
    def f(spec, path=None):
        if 'a' in spec:
            return AObj(spec, path=path)
        return obj_class(spec, path=path)
    f.__name__ = 'if_not_a_or_' + obj_class.__name__
    return f

class EObj(Base2):
    __fields__ = {
        'e1': dict(builder=child, child_builder=list_(if_not_a(BObj))),
        'e2': dict(builder=child, child_builder=if_not_a(map_(map_(AObj)))),
        'e3': dict(builder=child, child_builder=if_not_a(DObj)),
        'e4': dict(builder=child, child_builder=if_not_a(map_(AObj))),
    }

class FObj(AObj):
    __fields__ = {
        'f1': dict(builder=field),
    }

class GObj(Base2):
    __fields__ = {
        'a': dict(builder=child, child_builder=BObj),
        'b': dict(builder=child, child_builder=BObj),
        'c': dict(builder=child, child_builder=BObj),
    }

class HObj(Base2):
    __fields__ = {
        'a': dict(builder=field, key='b'),
    }

class IObj(AObj):
    __fields__ = {
        'a': dict(key='cc', builder=field),
    }

class JObj(Base2):
    __fields__ = {
        'a': dict(builder=field, restricted=True),
        'b': dict(builder=field, restricted=True, default='hi'),
    }

class KObj(Base2):
    __fields__ = {
        'a': dict(builder=field),
    }
KObj.attach_field('k1', builder=child, child_builder=KObj)


class Base2TestCase(unittest.TestCase):
    """ test case for base2.py """

    def test_field_meta(self):
        """ check FieldMeta
        """
        # should fill __child__ with fields created by builder:child
        self.assertEqual(AObj.__children__, ['c'])

    def test_field(self):
        """ make sure builder:field works
        """
        # default value is None
        self.assertEqual(AObj({}).a, None)
        self.assertEqual(AObj({'a': 1}).a, 1)

        # when required, raise exception when none
        self.assertRaises(Exception, lambda: AObj({}).b)
        self.assertEqual(AObj({'b': 2}).b, 2)

    def test_child(self):
        """ make sure builder:child works
        """
        # default is None
        self.assertEqual(AObj({}).c, None)
        self.assertNotEqual(AObj({'c':{}}).c, None)
        # child's field also created
        self.assertEqual(AObj({'c':{'bb':3}}).c.bb, 3)

    def test_map(self):
        """ make sure container:Map works
        """
        c = CObj({'cc':{'key1':{'a':1}, 'key2':{'b':2}}})
        self.assertTrue(issubclass(c.cc.__class__, _Map))
        self.assertTrue('key1' in c.cc)
        self.assertTrue(isinstance(c.cc['key1'], AObj))
        self.assertTrue('key2' in c.cc)
        self.assertTrue(isinstance(c.cc['key2'], AObj))
        self.assertEqual(c.cc['key1'].a, 1)
        self.assertEqual(c.cc['key2'].b, 2)

    def test_list(self):
        """ make sure container:List works
        """
        c = CObj({'ccc':[{'a':1}, {'a':2}]})
        self.assertTrue(issubclass(c.ccc.__class__, _List))
        cnt = {1: 0, 2:0}
        for e in c.ccc:
            cnt[e.a] += 1
        for c in cnt:
            self.assertEqual(cnt[c], 1)

    def test_composite_container(self):
        """ check child_builder=List(Map(List ....)
        """
        # map of list
        d = DObj({'d1':{'key1':[{'a':1},{'a':2}], 'key2':[{'a':3},{'a':4}]}})
        self.assertEqual(d.d1['key1'][0].a, 1)
        self.assertEqual(d.d1['key1'][1].a, 2)
        self.assertEqual(d.d1['key2'][0].a, 3)
        self.assertEqual(d.d1['key2'][1].a, 4)

        # list of map
        d = DObj({'d2': [{'key1':{'a':1}, 'key2':{'a':2}}, {'key3':{'a':3}, 'key4':{'a':4}}]})
        self.assertEqual(d.d2[0]['key1'].a, 1)
        self.assertEqual(d.d2[0]['key2'].a, 2)
        self.assertEqual(d.d2[1]['key3'].a, 3)
        self.assertEqual(d.d2[1]['key4'].a, 4)

        # map of map
        d = DObj({'d3': {'key1':{'key11':{'a':1}, 'key12':{'a':2}}, 'key2':{'key21':{'a':3}, 'key22':{'a':4}}}})
        self.assertEqual(d.d3['key1']['key11'].a, 1)
        self.assertEqual(d.d3['key1']['key12'].a, 2)
        self.assertEqual(d.d3['key2']['key21'].a, 3)
        self.assertEqual(d.d3['key2']['key22'].a, 4)

    def test_if_not_ref(self):
        """ make sure we can write a function as a selector to return expected type
        ex. Reference Object in OpenAPI 3.0 -> Some Object | Reference Object
        """
        e = EObj({'e1': [{'a':1}, {'bb':2}]})
        self.assertTrue(isinstance(e.e1[0], AObj))
        self.assertEqual(e.e1[0].a, 1)
        self.assertTrue(isinstance(e.e1[1], BObj))
        self.assertEqual(e.e1[1].bb, 2)

        # the case for Reference Object | Callbacs Object
        e = EObj({'e2': {'a': 1}})
        self.assertTrue(isinstance(e.e2, AObj))
        self.assertEqual(e.e2.a, 1)
        e = EObj({'e2': {'key1': {'key11': {'a':1}}, 'key2': {'key21': {'a':2}}}})
        self.assertFalse(isinstance(e.e2, AObj))
        self.assertEqual(e.e2['key1']['key11'].a, 1)
        self.assertEqual(e.e2['key2']['key21'].a, 2)

        # func as child_builder
        e = EObj({'e3': {'a': 1}})
        self.assertTrue(isinstance(e.e3, AObj))
        self.assertEqual(e.e3.a, 1)
        self.assertTrue(isinstance(EObj({'e3': {}}).e3, DObj))

        # funct with container
        e = EObj({'e4': {'a': 1}})
        self.assertTrue(isinstance(e.e4, AObj))
        self.assertEqual(e.e4.a, 1)
        e = EObj({'e4': {'key1': {'a':1}, 'key2': {'a':2}}})
        self.assertEqual(e.e4['key1'].a, 1)
        self.assertEqual(e.e4['key2'].a, 2)

    def test_inheritance(self):
        """ inheritance
        """
        # both fields are created
        f = FObj({'a':1, 'b': 2, 'f1':3})
        self.assertEqual(f.a, 1)
        self.assertEqual(f.b, 2)
        self.assertEqual(f.f1, 3)

    def test_compare(self):
        """ Base2Obj.compare
        """
        # when a field is different
        a1 = AObj({'a': 1})
        a2 = AObj({'a': 2})
        self.assertEqual(a1.compare(a2), (False, 'a'))

        # child field, missing, or different
        a1 = AObj({'c':{'bb':1}})
        a2 = AObj({})
        self.assertEqual(a1.compare(a2), (False, 'c'))
        a3 = AObj({'c':{'bb':2}})
        self.assertEqual(a1.compare(a3), (False, 'c/bb'))

        # _Map
        c1 = CObj({'cc':{'key1':{'a':1}, 'key2':{'b':2}}})
        c2 = CObj({'cc':{'key1':{'a':1}, 'key2':{'b':3}}})
        self.assertEqual(c1.compare(c2), (False, 'cc/key2/b'))

        # _List
        c1 = CObj({'ccc':[{'a':1, 'b':2}, {'a':2, 'b':3}]})
        c2 = CObj({'ccc':[{'a':1, 'b':2}, {'a':3 ,'b':3}]})
        self.assertEqual(c1.compare(c2), (False, 'ccc/1/a'))
        self.assertEqual(c1.compare(c1), (True, ''))
        self.assertEqual(c2.compare(c2), (True, ''))

        # _Map of _List
        d1 = DObj({'d1':{'key1':[{'b':1},{'b':2}], 'key2':[{'b':3},{'b':4}]}})
        d2 = DObj({'d1':{'key1':[{'b':1},{'b':3}], 'key2':[{'b':3},{'b':4}]}})
        d3 = DObj({'d1':{'key1':[{'b':1},{'b':2}]}})
        self.assertEqual(d1.compare(d2), (False, 'd1/key1/1/b'))
        self.assertEqual(d1.compare(d3), (False, 'd1/key2'))
        self.assertEqual(d1.compare(d1), (True, ''))
        self.assertEqual(d2.compare(d2), (True, ''))
        self.assertEqual(d3.compare(d3), (True, ''))

        # _List of _Map
        d1 = DObj({'d2': [{'key1':{'b':1}, 'key2':{'b':2}}, {'key3':{'b':3}, 'key4':{'b':4}}]})
        d2 = DObj({'d2': [{'key1':{'b':1}, 'key2':{'b':2}}, {'key3':{'b':3}, 'key4':{'b':5}}]})
        d3 = DObj({'d2': [{'key1':{'b':1}}, {'key3':{'b':3}, 'key4':{'b':4}}]})
        self.assertEqual(d1.compare(d2), (False, 'd2/1/key4/b'))
        self.assertEqual(d1.compare(d3), (False, 'd2/0/key2'))
        self.assertEqual(d1.compare(d1), (True, ''))
        self.assertEqual(d2.compare(d2), (True, ''))
        self.assertEqual(d3.compare(d3), (True, ''))

        # _Map of _Map
        d1 = DObj({'d3': {'key1':{'key11':{'b':1}, 'key12':{'b':2}}, 'key2':{'key21':{'b':3}, 'key22':{'b':4}}}})
        d2 = DObj({'d3': {'key1':{'key11':{'b':1}, 'key12':{'b':2}}, 'key2':{'key21':{'b':3}, 'key22':{'b':5}}}})
        d3 = DObj({'d3': {'key1':{'key11':{'b':1}, 'key12':{'b':2}}, 'key2':{'key21':{'b':3}}}})
        self.assertEqual(d1.compare(d2), (False, 'd3/key2/key22/b'))
        self.assertEqual(d1.compare(d3), (False, 'd3/key2/key22'))
        self.assertEqual(d1.compare(d1), (True, ''))
        self.assertEqual(d2.compare(d2), (True, ''))
        self.assertEqual(d3.compare(d3), (True, ''))

        # dict
        a1 = AObj({'b':{'a':1,'b':2}})
        a2 = AObj({'b':{'a':2,'b':2}})
        a3 = AObj({'b':{'a':1}})
        self.assertEqual(a1.compare(a2), (False, 'b/a'))
        self.assertEqual(a1.compare(a3), (False, 'b/b'))
        self.assertEqual(a1.compare(a1), (True, ''))
        self.assertEqual(a2.compare(a2), (True, ''))
        self.assertEqual(a3.compare(a3), (True, ''))

        # list
        a1 = AObj({'b':[1,2,3]})
        a2 = AObj({'b':[1,2,4]})
        self.assertEqual(a1.compare(a2), (False, 'b/2'))
        self.assertEqual(a1.compare(a1), (True, ''))
        self.assertEqual(a2.compare(a2), (True, ''))

    def test_attach_child(self):
        """ Base2Obj.attach_child
        """
        a1 = AObj({})
        a1.attach_child('c', BObj({'bb':1}))
        self.assertEqual(a1.c.bb, 1)

    def test_dump(self):
        """ [Base2Obj, _Map, _List].dump
        """
        o = {'b':1}
        a = AObj(o)
        self.assertEqual(a.dump(), o)

        o = {'b':1, 'c':{'bb':2}}
        a = AObj(o)
        self.assertEqual(a.dump(), o)
        # children first
        a.attach_child('c', BObj({'bb':3}))
        self.assertEqual(a.dump(), {'b':1, 'c':{'bb':3}})

        # _Map
        o = {'cc':{'key1':{'b':1}, 'key2':{'b':2}}}
        c = CObj(o)
        self.assertEqual(c.dump(), o)
        # modify map
        c.cc['key3'] = AObj({'b':3})
        self.assertEqual(c.dump(), {'cc':{'key1':{'b':1}, 'key2':{'b':2}, 'key3':{'b':3}}})
        # replace child
        c.attach_child('cc', map_(AObj)({'key3':{'b':1}}))
        self.assertEqual(c.dump(), {'cc':{'key3':{'b':1}}})

        # _List
        o = {'ccc':[{'a':1, 'b':2}, {'a':2, 'b':3}]}
        c = CObj(o)
        self.assertEqual(c.dump(), o)
        # modify list
        c.ccc.append(AObj({'b':4}))
        self.assertEqual(c.dump(), {'ccc':[{'a':1, 'b':2}, {'a':2, 'b':3}, {'b':4}]})
        # replace child
        c.attach_child('ccc', list_(AObj)([{'b':1}, {'b':4}]))
        self.assertEqual(c.dump(), {'ccc':[{'b':1}, {'b':4}]})

    def test_resolve(self):
        """ [Base2Obj, _Map, _List].resolve
        """
        # Base2Obj
        a = AObj({'a':1, 'c':{'bb':2}})
        self.assertEqual(a.resolve('a'), 1)
        c = a.resolve('c')
        self.assertTrue(isinstance(c, BObj))
        self.assertEqual(c.resolve('bb'), 2)
        self.assertEqual(a.resolve(['c', 'bb']), 2)

        # _Map
        c = CObj({'cc':{'key1':{'a':1}, 'key2':{'b':2}}})
        self.assertEqual(c.resolve(['cc', 'key2', 'b']), 2)
        m = c.resolve('cc')
        self.assertTrue(issubclass(m.__class__, _Map))
        self.assertEqual(m.resolve(['key1', 'a']), 1)

        # _List
        c = CObj({'ccc':[{'a':1, 'b':2}, {'a':2, 'b':3}]})
        self.assertEqual(c.resolve(['ccc', '1', 'a']), 2)
        l = c.resolve('ccc')
        self.assertTrue(issubclass(l.__class__, _List))
        self.assertEqual(l.resolve(['0', 'b']), 2)

        # _Map of _List
        d = DObj({'d1':{'key1':[{'b':1},{'b':2}], 'key2':[{'b':3},{'b':4}]}})
        self.assertEqual(d.resolve(['d1', 'key2', '1', 'b']), 4)

        # _List of _Map
        d = DObj({'d2': [{'key1':{'b':1}, 'key2':{'b':2}}, {'key3':{'b':3}, 'key4':{'b':4}}]})
        self.assertEqual(d.resolve(['d2', '1', 'key4', 'b']), 4)

        # _Map of _Map
        d = DObj({'d3': {'key1':{'key11':{'b':1}, 'key12':{'b':2}}, 'key2':{'key21':{'b':3}, 'key22':{'b':4}}}})
        self.assertEqual(d.resolve(['d3', 'key2', 'key21', 'b']), 3)

        # dict
        a = AObj({'b':{'a':1,'b':2}})
        self.assertEqual(a.resolve(['b', 'a']), 1)

        # list
        a = AObj({'b':[1,2,3]})
        self.assertEqual(a.resolve(['b', '0']), 1)

    def test_merge_children(self):
        """ Base2Obj.merge_children
        """
        g1 = GObj({'a': {'bb':'a'}})
        self.assertEqual(g1._children_.keys(), ['a'])
        g2 = GObj({'b': {'bb':'b'}})
        g1.merge_children(g2)
        self.assertEqual(g1._children_.keys(), ['a', 'b'])
        self.assertEqual(g2._children_.keys(), ['b'])

    def test_key_and_name_different(self):
        """ property name of key to underlying dict can be different
        """
        h = HObj({'a':1, 'b':2})
        self.assertEqual(h.a, 2) # should be the value of 'b'

    def test_inherit_overwrite_fields(self):
        """ when inheriting, child's field would overwrite parent's
        """
        i = IObj({'a':1, 'cc':100})
        self.assertEqual(i.a, 100)

    def test_field_restricted(self):
        """ when restricted, should not existed in key
        """
        j = JObj({'a':1, 'b':1})
        self.assertRaises(Exception, getattr, j, 'a')
        self.assertRaises(Exception, getattr, j, 'b')
        j = JObj({})
        # could access 'b' because of default
        self.assertEqual(j.b, 'hi')

    def test_recursive_field(self):
        """ field reference to self
        """
        k = KObj({'k1':{'k1':{'k1':{'a':2}}}, 'a':1})
        self.assertTrue(isinstance(k, KObj))
        self.assertEqual(k.a, 1)
        self.assertTrue(isinstance(k.k1, KObj))
        self.assertTrue(isinstance(k.k1.k1, KObj))
        self.assertEqual(k.k1.k1.k1.a, 2)

    def test_path(self):
        """ validate path property
        """
        # child field, missing, or different
        a = AObj({'c':{'bb':1}})
        self.assertEqual(a.path, None)
        self.assertEqual(a.c.path, 'c')

        # _Map
        c = CObj({'cc':{'key1':{'a':1}, 'key2':{'b':2}}})
        self.assertEqual(c.cc['key1'].path, 'cc/key1')

        # _List
        c = CObj({'ccc':[{'a':1, 'b':2}, {'a':2, 'b':3}]})
        self.assertEqual(c.ccc[0].path, 'ccc/0')

        # _Map of _List
        d = DObj({'d1':{'key1':[{'b':1},{'b':2}], 'key2':[{'b':3},{'b':4}]}})
        self.assertEqual(d.d1['key1'][0].path, 'd1/key1/0')

        # _List of _Map
        d = DObj({'d2': [{'key1':{'b':1}, 'key2':{'b':2}}, {'key3':{'b':3}, 'key4':{'b':4}}]})
        self.assertEqual(d.d2[0]['key1'].path, 'd2/0/key1')

        # _Map of _Map
        d = DObj({'d3': {'key1':{'key11':{'b':1}, 'key12':{'b':2}}, 'key2':{'key21':{'b':3}, 'key22':{'b':4}}}})
        self.assertEqual(d.d3['key1']['key11'].path, 'd3/key1/key11')

