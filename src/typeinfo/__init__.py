""" 
    contains utilities and definitions of the BC attribute type information container. Use in your class as follows:
    class SomeClass(object):
        __typeinfo__ = TypeInfo(
                    att1=int,
                    att2=unicode
                                 )
        def __init__(self):
           self.att1=1
           self.att2="A"
"""

settings = dict(
DEBUG_MODE = False
)

import functools
from inspect import isclass, ismethod, isfunction
from copy import deepcopy
from base import TypedObjectBase, TypedObjectMetaClass, MemberTypeInfo



class TypedObject(TypedObjectBase):
    """ Inherit from this class to get your type info auto generated based on member types in you class object.
        Ex:
            Class A(TypedObject):
                i : int,
                j : string

            this class member info will be intialized to have two members i & j of type string and int
    """

    __metaclass__ = TypedObjectMetaClass


    def __init__(self):
        self.initMembers()



class IntegerType(MemberTypeInfo):

    def __init__(self,**kwargs):
        kwargs["type"]=(int,long)
        super(IntegerType,self).__init__(**kwargs)


class NonNullable(MemberTypeInfo):
    def __init__(self,type=None,**kwargs):
        kwargs["type"] = type
        kwargs["nullable"] = False
        super(NonNullable,self).__init__(**kwargs)

