""" 
    contains utilities and definitions of the BC attribute type information container. Use in ure class as follows:
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

class TypeException(Exception):
    pass

class MemberTypeInfo():
    """ Contains the type info of members. Things like:
        Type
        Nullable
        Default value
        Ordering in display/enumeration
    """
    def __init__(self,name=None,type=None,nullable=True,defval=None,order=None):
        self.name=name        
        self.type=type
        self.nullable=nullable
        self.defval=defval
        self.order = order
        
    def validateSettings(self):
        if self.name is None:
            raise TypeException("MemberTypeInfo: name is not specified")

        if self.type is None:
            raise TypeException("MemberTypeInfo for %s: type is not specified" % self.name)
        if not self.nullable and self.defval is None:
            raise TypeException("MemberTypeInfo for %s: member is not nullable but defval is set to None" % self.name)

    def validateValue(self,val):
        if val is None and not self.nullable:
            raise TypeException("Member '%s' may not be null" % self.name)
        if val is not None and not isinstance(val,self.type):
            raise TypeException("Memeber '%s' is not derived from '%s'." % (self.name,self.type))


    def __cmp__(self, other):
        if not isinstance(other,MemberTypeInfo):
            raise Exception("Cain't compare a MemberTypeInfo to %s",other)

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
                raise TypeException("TypeInfo - failed to initialize MemberTypeInfo with %s",asList[i])

            mti.validateSettings()
            if mti.order is None: mti.order=i
            self._memberInfo[mti.name]=mti
        
        for name,value in kwargs.iteritems():

            value = normalizeMti(value)
            if not isinstance(value,MemberTypeInfo):
                raise TypeException("TypeInfo - failed to initialize MemberTypeInfo for %s",name)
            value.name=name
            value.validateSettings()
            self._memberInfo[value.name]=value





class TypedObject(object):
    """ mixing class containing all kind of type info utils """

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






    def enumTypes(self):
        """ Enumerates the attributes and types of an object. return is a enum of tuples (attname,atttype) """
        return [(mti.name,mti.type) for mti in TypedObject._getTypeInfoList(self)]

    def initToNone(self):
        """ set all typed attributes to None. Note- this will throw and exception of not members are nullable """
        for att in TypedObject._getTypeInfoDict(self).keys():
            setattr(self,att,None)

    def initToDefaults(self):
        """ set all typed attributes to their default values. Note all types must have a default constructor """
        for mti in TypedObject._getTypeInfoDict(self).values():
            setattr(self,mti.name,mti.defval)

    def validateTypes(self,allowNone=True,throw=True):
        """ scans all typed attributes of obj to see if the derive from or are the types mentioned. """
        for mti in TypedObject._getTypeInfoDict(self).values():
            val = getattr(self,mti.name)
            if not isinstance(val,mti.type):
                if throw:
                    raise TypeException("Member %s is not of type %s (found %s)",mti.name,mti.type,val)

                else:
                    return False




