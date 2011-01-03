import collections

def simplify(a, b):
    res = collections.defaultdict(int, a)
    for k in b:
        res[k] += b[k]
    for k in res.keys():
        if res[k] == 0:
            del res[k]
    return dict(res)

def invert(u):
    res = dict(u)
    for k in res:
        res[k] *= -1
    return res

def unit(units):
    return UnitMeta("unit", (Unitless,), {"units":units})

class UnitMeta(type):
    BaseUnit = None #breaking circular reference
    _unit_type_reg = {}
    
    def __new__(cls, name, bases, attr):
        if cls.BaseUnit is None: #if not yet initialized
            return type.__new__(cls, name, bases, attr)
        if cls.BaseUnit in bases: #creating a new base unit
            newcls = type.__new__(cls, name, bases, attr)
            newcls.units = getattr(cls, "units", {})
            newcls.units[newcls] = 1
            key = frozenset(newcls.units.items())
            cls._unit_type_reg[key] = newcls
        else: #otherwise, check for already created
            key = frozenset(attr["units"].items())
            if key not in cls._unit_type_reg:
                cls._unit_type_reg[key] = type.__new__(cls, name, bases, attr)
        return cls._unit_type_reg[key]
    
    def __rmul__(cls, other):
        if isinstance(other, (cls.BaseUnit, UnitMeta)):
            newcls = unit(simplify(cls.units, other.units))
            if isinstance(other, cls.BaseUnit):
                return newcls(other.value)
            return newcls
        elif isinstance(other, (int, long, float)):
            return cls(other)
        raise TypeError() #figure out good error message

    __mul__ = __rmul__
    
    def __div__(cls, other):
        return cls*(other**-1)
    
    def __rdiv__(cls, other):
        return (cls**-1)*other
    
    def __pow__(cls, pow):
        return unit(dict([(k,pow*v) for k,v in cls.units.items()]))

class BaseUnit(object):
    __metaclass__ = UnitMeta
    
    def __init__(self, value):
        self.value = value
    
    def __add__(self, other):
        if self.__class__ == other.__class__:
            return self.__class__(self.value + other.value)
        raise TypeError() #figure out good error message
    
    def __sub__(self, other):
        if self.__class__ == other.__class__:
            return self.__class__(self.value - other.value)
        raise TypeError() #figure out good error message
    
    def __mul__(self, other):
        if isinstance(other, BaseUnit):
            return (self.__class__ * other.__class__)(self.value*other.value)
        elif isinstance(other, UnitMeta):
            return UnitMeta.__mul__(other, self)
        elif isinstance(other, (int, long, float)):
            return self.__class__(self.value*other)
        raise TypeError() #figure out a good error message
    
    __rmul__ = __mul__
    
    def __div__(self, other):
        return self*(other**-1)
    
    def __rdiv__(self, other):
        return (self**-1)*other
    
    def __pow__(self, pow):
        return (self.__class__**pow)(self.value**pow)

class Unitless(BaseUnit):
    units = {}

UnitMeta._unit_type_reg[frozenset([])] = Unitless
UnitMeta.BaseUnit = BaseUnit
    
class meter(BaseUnit): pass

class second(BaseUnit): pass



