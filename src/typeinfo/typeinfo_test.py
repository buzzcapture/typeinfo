from TypeInfo import TypedObject, TypeInfo, MemberTypeInfo, TypeException

__author__ = 'boaz'

import unittest


class MyTestCase(unittest.TestCase):
    def test_list_simple(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo(
                i = int,
                j = MemberTypeInfo(type=str,default="a"),
            )

        en = A().listTypes()
        self.assertEqual(en, [("i" , int),("j", str)])

    def test_set_to_default(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo(
                i = int,
                j = MemberTypeInfo(type=str,default="a"),
            )

        en = A()
        en.initToDefaults()
        self.assertEqual(en.i, None)
        self.assertEqual(en.j, "a")

    def test_set_to_none(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo(
                i = int,
                j = MemberTypeInfo(type=str,default="a"),
            )

        en = A()
        en.initToNone()
        self.assertEqual(en.i, None)
        self.assertEqual(en.j, None)



    def test_list_multiple_base_classes(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo(
                i = int,
            )

        class B(TypedObject):
            __typeinfo__= TypeInfo(
                j = MemberTypeInfo(type=str,default="a"),
                z = MemberTypeInfo(type=str,default="a"),
            )


        class C(A,B):
            __typeinfo__= TypeInfo(
                k =int,
                z = int
            )

        en = C().listTypes()
        self.assertEqual(en, [("i" , int),("j", str),("k",int),("z",int)])



    def test_list_order(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo(
                i = int,
                j = MemberTypeInfo(type=str,default="a"),
                y = MemberTypeInfo(type=int,default=1,order=0),
                a = MemberTypeInfo(type=int,default=1,order=0),
                c = MemberTypeInfo(type=int,default=1,order=1),
            )

        en = A().listTypes()
        self.assertEqual([n for n,t in en], ["a","y","c","i","j"])



    def test_list_list_init(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo([
                ("i" , int),
                { "name":"y" , "type" : str, "default" : "a" },
                MemberTypeInfo(name="j",type=int,default=1),
            ])

        en = A().listTypes()
        self.assertEqual([n for n,t in en], ["i","y","j"])

    def test_exceptions(self):
        class A(TypedObject):
            __typeinfo__ = TypeInfo(
                i = MemberTypeInfo(type=str, nullable=False, default='nothing!'),
            )

        a = A()
        self.assertRaises(TypeException, a.initToNone)

        self.assertRaises(TypeException, TypeInfo, i=MemberTypeInfo(type=str, nullable=False, default=None))

    def test_defaults_not_shared(self):
        class A(TypedObject):
            __typeinfo__ = TypeInfo(
                i = MemberTypeInfo(type=list, default=[])
            )
        a = A()
        b = A()

        a.initToDefaults()
        a.i.append(1)
        b.initToDefaults()
        self.assertEqual(b.i, [])

if __name__ == '__main__':
    unittest.main()
