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
import functools
from inspect import isclass, ismethod, isfunction
from copy import deepcopy
from types import MethodType


DEBUG_MODE = __debug__


class TypeException(Exception):
    pass

class MemberTypeInfo():
    """ Contains the type info of members. Things like:
        Type
        Nullable
        Default value
        Ordering in display/enumeration
    """
    def __init__(self,name=None,type=None,nullable=True,default=None,order=None):
        self.name=name        
        self.type=type
        self.nullable=nullable
        self.default = default
        self.order = order
        
    def validateSettings(self):
        if self.name is None:
            raise TypeException("MemberTypeInfo: name is not specified")

        if self.type is None:
            raise TypeException("MemberTypeInfo for %s: type is not specified" % self.name)
        if not isclass(self.type):
            raise TypeException("MemberTypeInfo for %s: type is not a class" % self.name)
        if not self.nullable and self.default is None:
            raise TypeException("MemberTypeInfo for %s: member is not nullable but default is set to None" % self.name)

    def validateValue(self,val):
        if val is None and not self.nullable:
            raise TypeException("Member '%s' may not be null" % self.name)
        if val is not None and not isinstance(val,self.type):
            raise TypeException("Memeber '%s' is not derived from '%s'." % (self.name,self.type))


    def __cmp__(self, other):
        if not isinstance(other,MemberTypeInfo):
            raise Exception("Can't compare a MemberTypeInfo to %s",other)

        if self.order is not None:
            if other.order is None:
                return -1; # things with order come before other stuff
            i = cmp(self.order,other.order)
            if i !=0:
                return i;
            return cmp(self.name,other.name)

        if other.order is not None:
            return 1 # things with order come before other stuff

        return cmp(self.name,other.name)


class TypeInfo(object):
    def __init__(self,asList=[],**kwargs):
        """ asList = a list of:
                - tuples/list to be used as arguments to the MemberTypInfo constractor
                - a dict to be used as keywords arguments to the MemberTypeInfo
                - MemberTypeInfo instance

          **kwargs can be use to specify things in a more python like style
        """
        self._memberInfo = {}

        def normalizeMti(mti):
            if isinstance(mti,tuple) or isinstance(mti,list):
                return MemberTypeInfo(*mti)
            elif isinstance(mti,dict):
                return MemberTypeInfo(**mti)
            elif isclass(mti):
                return MemberTypeInfo(type=mti)
            elif  isinstance(mti,MemberTypeInfo):
                return mti


            return None

        
        for i in range(len(asList)):
            mti = normalizeMti(asList[i])

            if not isinstance(mti, MemberTypeInfo):
                raise TypeException("TypeInfo - failed to initialize MemberTypeInfo with %s" % asList[i])

            mti.validateSettings()
            if mti.order is None: mti.order=i
            self._memberInfo[mti.name]=mti
        
        for name,value in kwargs.iteritems():

            value = normalizeMti(value)
            if not isinstance(value,MemberTypeInfo):
                raise TypeException("TypeInfo - failed to initialize MemberTypeInfo for %s" % name)
            value.name=name
            value.validateSettings()
            self._memberInfo[value.name]=value


class class_or_instance(object):
    def __init__(self, func):
        self._func = func

    def __get__(self, obj, cls):
        return MethodType(self._func, cls if obj is None else obj, cls)


class TypedObjectBase(object):
    """ mixin class containing all kind of type info utils """

    @staticmethod
    def _getTypeInfoDict(obj):
        ret = {}

        if not isclass(obj):
            obj=type(obj)

        for base in reversed(obj.__bases__):
            # walking in reverse to mimic attribute lookup semantics """
            bd = TypedObject._getTypeInfoDict(base)
            ret.update(bd)


        if hasattr(obj,"__typeinfo__"):
            ret.update(obj.__typeinfo__._memberInfo)

        return ret


    @staticmethod
    def _getTypeInfoList(obj):
        ret  = TypedObject._getTypeInfoDict(obj).values()
        ret.sort()
        return ret

    @class_or_instance
    def listTypes(self):
        """ Enumerates the attributes and types of an object. return is a list of tuples (attname,atttype) """
        return [(mti.name,mti.type) for mti in TypedObject._getTypeInfoList(self)]

    def initToNone(self):
        """ Set all typed attributes to None. Note: this will throw an exception if any members are not nullable """
        for att,mti in TypedObject._getTypeInfoDict(self).items():
            if not mti.nullable:
                raise TypeException('Member %s is not nullable' % att)
            setattr(self,att,None)

    def initToDefaults(self):
        """ set all typed attributes to their default values. Note all types must have a default """
        for mti in TypedObject._getTypeInfoDict(self).values():
            setattr(self,mti.name,deepcopy(mti.default))

    def validateMemberTypes(self,throw=True):
        """ scans all typed attributes of obj to see if the derive from or are the types mentioned. """
        for mti in TypedObject._getTypeInfoDict(self).values():
            val = getattr(self, mti.name)
            if val is None:
                if not mti.nullable:
                    raise TypeException('Member %s of %s is not nullable but is None' % mti.name,self)
            elif not isinstance(val,mti.type):
                if throw:
                    raise TypeException("Member %s of %s is not of type %s (found %s)" % (mti.name,self,mti.type,val))
                else:
                    return False
        return True

    def initFromDict(self, initDict=None, **kwargs):
        if initDict is not None:
            kwargs.update(initDict)
        for (k,v) in kwargs.items():
            setattr(self, k, v)

def _auto_input_checker(func):

    def test(o):
        if isinstance(o,TypedObjectBase):
            o.validateMemberTypes()

    @functools.wraps(func)
    def checker(*args,**kwargs):
        """ also checks self as it is the first param """
        for a in args: test(a)
        for a in kwargs.values(): test(a)

        r = func(*args,**kwargs)
        return r

    return checker

def _auto_output_checker(func):

    def test(o):
        if isinstance(o,TypedObjectBase):
            o.validateMemberTypes()

    @functools.wraps(func)
    def checker(*args,**kwargs):
        """ also checks self as it is the first param """

        r = func(*args,**kwargs)
        if args: test(args[0]) # test self if there
        test(r)

        return r

    return checker


class TypedObjectMetaClass(type):

     def __new__(cls, name, bases, attrs):
        meta_info = dict()

        def istypeinfo(att,value):
            return  (not (att.startswith("__") and att.endswith("__"))) and (isclass(value) or isinstance(value,MemberTypeInfo))

        for (k,v) in attrs.iteritems():
            if istypeinfo(k,v):
                meta_info[k]=v
            if DEBUG_MODE and isfunction(v):
                if k == "__init__":
                    attrs[k]=_auto_output_checker(v)
                else:
                    attrs[k]=_auto_output_checker(_auto_input_checker(v))


        if len(meta_info):
            for k in meta_info.keys():
                del attrs[k]
            mi = TypeInfo(**meta_info)
            attrs["__typeinfo__"] = mi

        return type.__new__(cls, name, bases, attrs)

     

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
        self.initToDefaults()



                 
