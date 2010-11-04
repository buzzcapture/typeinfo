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
from inspect import isclass
from copy import deepcopy
from type import MethodType

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


class TypedObject(object):
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

    def validateMemberTypes(self,allowNone=True,throw=True):
        """ scans all typed attributes of obj to see if the derive from or are the types mentioned. """
        for mti in TypedObject._getTypeInfoDict(self).values():
            val = getattr(self, mti.name)
            if val is None:
                if not mti.nullable:
                    raise TypeException('Member %s is not nullable but is None' % mti.name)
            elif not isinstance(val,mti.type):
                if throw:
                    raise TypeException("Member %s is not of type %s (found %s)" % (mti.name,mti.type,val))
                else:
                    return False
        return True