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
    num = [(k,v) for k,v in units.items() if v > 0]
    den = [(k,v) for k,v in units.items() if v < 0]
    numerator = "*".join([k.abbreviation+("**"+str(v) if v != 1 else "")
                          for k,v in num])
    if len(den) != 0:
        if len(num) > 1:
            numerator = "("+numerator+")"
        denominator = "*".join([k.abbreviation+("**"+str(-v) if v != -1 else "")
                                for k,v in den])
        if len(den) > 1:
            denominator = "("+denominator+")"
        if len(num) != 0:
            name = "*"+numerator+"/"+denominator
        else:
            name = "/"+denominator
    else:
        name = "*"+numerator
    return UnitMeta(name, (Derived,), {"units":units})

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
        return cls(other)

    __mul__ = __rmul__
    
    def __div__(cls, other):
        return cls*(other**-1)
    
    def __rdiv__(cls, other):
        return (cls**-1)*other
    
    def __pow__(cls, pow):
        return unit(dict([(k,pow*v) for k,v in cls.units.items()]))

class BaseUnit(object):
    __metaclass__ = UnitMeta
    
    @property
    def abbreviation(self):
        return self.__class__.__name__
    
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
        return self.__class__(self.value*other)
    
    __rmul__ = __mul__
    
    def __div__(self, other):
        return self*(other**-1)
    
    def __rdiv__(self, other):
        return (self**-1)*other
    
    def __pow__(self, pow):
        return (self.__class__**pow)(self.value**pow)
    
    def __repr__(self):
        return repr(self.value)+"*"+self.abbreviation
    
    __array_priority__ = 10.0 #for numpy compatibility -- ensure [1,2]*m not [1*m, 2*m]

class Derived(BaseUnit):
    def __repr__(self):
        return repr(self.value)+self.abbreviation

class Unitless(Derived):
    units = {}
    
    def __new__(cls, value):
        return value #Unitless things get unwrapped

UnitMeta._unit_type_reg[frozenset([])] = Unitless
UnitMeta.BaseUnit = BaseUnit
    
class meter   (BaseUnit): abbreviation = "m"
class second  (BaseUnit): abbreviation = "s"
class kilogram(BaseUnit): abbreviation = "kg"
class Ampere  (BaseUnit): abbreviation = "A"
class mole    (BaseUnit): abbreviation = "mol"
class kelvin  (BaseUnit): abbreviation = "K" 
class candela (BaseUnit): abbreviation = "cd"
m = meter; s = second; kg = kilogram; A = Ampere; mol = mole
K = kelvin; cd = candela

class Newton(Derived):
    units = {kilogram:1, meter:1, second:-2}
    abbreviation = "N"
N = Newton
Joule   = N * m  ; Joule  .__name__ = "Joule"  ; Joule  .abbreviation = "J"
J = Joule
Watt    = J / s  ; Watt   .__name__ = "Watt"   ; Watt   .abbreviation = "W"
W = Watt
Coloumb = A * s  ; Coloumb.__name__ = "Coloumb"; Coloumb.abbreviation = "C"
C = Coloumb
