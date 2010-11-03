from TypeInfo import TypedObject, TypeInfo, MemberTypeInfo

__author__ = 'boaz'

import unittest


class MyTestCase(unittest.TestCase):
    def test_enum_simple(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo(
                i = int,
                j = MemberTypeInfo(type=str,defval="a"),
            )

        en = A().enumTypes()
        self.assertEqual(en, [("i" , int),("j", str)])

    def test_enum_set_to_default(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo(
                i = int,
                j = MemberTypeInfo(type=str,defval="a"),
            )

        en = A()
        en.initToDefaults()
        self.assertEqual(en.i, None)
        self.assertEqual(en.j, "a")

    def test_enum_set_to_none(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo(
                i = int,
                j = MemberTypeInfo(type=str,defval="a"),
            )

        en = A()
        en.initToNone()
        self.assertEqual(en.i, None)
        self.assertEqual(en.j, None)



    def test_enum_multiple_base_classes(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo(
                i = int,
            )

        class B(TypedObject):
            __typeinfo__= TypeInfo(
                j = MemberTypeInfo(type=str,defval="a"),
                z = MemberTypeInfo(type=str,defval="a"),
            )


        class C(A,B):
            __typeinfo__= TypeInfo(
                k =int,
                z = int
            )

        en = C().enumTypes()
        self.assertEqual(en, [("i" , int),("j", str),("k",int),("z",int)])



    def test_enum_order(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo(
                i = int,
                j = MemberTypeInfo(type=str,defval="a"),
                y = MemberTypeInfo(type=int,defval=1,order=0),
                a = MemberTypeInfo(type=int,defval=1,order=0),
                c = MemberTypeInfo(type=int,defval=1,order=1),
            )

        en = A().enumTypes()
        self.assertEqual([n for n,t in en], ["a","y","c","i","j"])



    def test_enum_list_init(self):

        class A(TypedObject):
            __typeinfo__= TypeInfo([
                ("i" , int),
                { "name":"y" , "type" : str, "defval" : "a" },
                MemberTypeInfo(name="j",type=int,defval=1),
            ])

        en = A().enumTypes()
        self.assertEqual([n for n,t in en], ["i","y","j"])



if __name__ == '__main__':
    unittest.main()
