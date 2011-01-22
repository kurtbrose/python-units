import collections
import decimal
import operator
import math

def bits(n):
    mask = 1<<int(math.floor(math.log(n, 2)))
    while mask != 0:
        yield 1 if mask & n else 0
        mask >>= 1

class Decimal_Float(decimal.Decimal):
    '''
    This class is a value that doesn't know if it should be a Decimal or a float
    yet.  The first thing that touches it with an arithmetic operation will
    decide for it.
    '''
    def _do_op(self, other, op, r=False):
        #if this is "right side" operation, reverse arg order
        _op = (lambda a,b: op(b,a)) if r else op
        if isinstance(other, self.__class__):
            return self.__class__(_op(decimal.Decimal(self), other))
        if isinstance(other, decimal.Decimal):
            return _op(decimal.Decimal(self), other)
        if other%1 == 0 and self%1 == 0:
            return _op(int(self), other)
        return _op(float(self), other)
    
    def __add__(self, other): return self._do_op(other, operator.add)
    def __sub__(self, other): return self._do_op(other, operator.sub)
    def __mul__(self, other): return self._do_op(other, operator.mul)
    def __div__(self, other): return self._do_op(other, operator.div)
    def __gt__(self, other): return self._do_op(other, operator.gt)
    def __lt__(self, other): return self._do_op(other, operator.lt)
    
    def __radd__(self, other): return self._do_op(other, operator.add, r=True)
    def __rsub__(self, other): return self._do_op(other, operator.sub, r=True)
    def __rmul__(self, other): return self._do_op(other, operator.mul, r=True)
    def __rdiv__(self, other): return self._do_op(other, operator.div, r=True)
    
    def __pow__(self, other): 
        if self%1 == 0 and other%1 == 0 and other > 0:
            return self.__class__(int(int(self)**int(other)))
        if other%1 == 0:
            o = other if other > 0 else -other
            acc = self.__class__(1)
            if other == 0: return acc
            for b in bits(int(o)):
                acc *= acc
                if b: acc *= self
            return acc if other > 0 else self.__class__(1)/acc
        return float(self)**other
    
    def __repr__(self): return "Decimal_Float('"+str(self)+"')"

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

def unit(scale, units):
    num = [(k,v) for k,v in units.items() if v > 0]
    den = [(k,v) for k,v in units.items() if v < 0]
    numerator = "*".join([k.abbrev()+("**"+str(v) if v != 1 else "")
                          for k,v in num])
    if len(den) != 0:
        if len(num) > 1:
            numerator = "("+numerator+")"
        denominator = "*".join([k.abbrev()+("**"+str(-v) if v != -1 else "")
                                for k,v in den])
        if len(den) > 1:
            denominator = "("+denominator+")"
        if len(num) != 0:
            name = "*"+numerator+"/"+denominator
        else:
            name = "/"+denominator
    else:
        name = "*"+numerator
    if scale != 1:
        name = "*("+str(scale)+")"+name
    return UnitMeta(name, (Derived,), {"units":units, "scale":scale})

class UnitMeta(type):
    BaseUnit = None #breaking circular reference
    _unit_type_reg = {}
    
    def __new__(cls, name, bases, attr):
        if cls.BaseUnit is None: #if not yet initialized
            return type.__new__(cls, name, bases, attr)
        if cls.BaseUnit in bases: #creating a new base unit
            newcls = type.__new__(cls, name, bases, attr)
            newcls.units = {}
            newcls.units[newcls] = 1
            key = newcls._scale, frozenset(newcls.units.items())
            cls._unit_type_reg[key] = newcls
        elif attr["units"] == {}:
            return attr["scale"]
        else: #otherwise, check for already created
            attr.setdefault("scale", Decimal_Float(1))
            key = attr["scale"], frozenset(attr["units"].items())
            if key not in cls._unit_type_reg:
                cls._unit_type_reg[key] = type.__new__(cls, name, bases, attr)
        return cls._unit_type_reg[key]
    
    def __rmul__(cls, other):
        if isinstance(other, (cls.BaseUnit, UnitMeta)):
            newcls = unit(cls.scale * other.scale, simplify(cls.units, other.units))
            if isinstance(other, cls.BaseUnit):
                if isinstance(newcls, UnitMeta):
                    return newcls(other.value)
                else:
                    return newcls * other.value
            return newcls
        return cls(other)

    __mul__ = __rmul__
    
    def __div__(cls, other):
        return cls*(other**-1)
    
    def __rdiv__(cls, other):
        return (cls**-1)*other
    
    def __pow__(cls, pow):
        if pow == 0:
            return Unitless
        return unit(cls.scale**pow, dict([(k,pow*v) for k,v in cls.units.items()]))
    
    def __reduce__(cls):
        #this will work once issue 7689 is fixed http://bugs.python.org/issue7689
        return UnitMeta, (cls.__name__, cls.__bases__, cls.__dict__)

def unit_unpickler(value, *a):
    return UnitMeta(*a)(value)

class BaseUnit(object):
    __metaclass__ = UnitMeta
    scale = Decimal_Float(1)
    
    @classmethod
    def abbrev(cls):
        return getattr(cls, "abbreviation", cls.__name__)
    
    @classmethod
    def _scale(cls, other):
        '''
        _scale another Unit instance's value to be in terms of this Unit instance
        '''
        if cls.units == other.units:
            factor = other.scale / cls.scale
            return other.value*factor
        raise TypeError() #figure out a good error message
    
    def __init__(self, value):
        self.value = value
    
    def __add__(self, other):
        if self.__class__ == other.__class__:
            return self.__class__(self.value + other.value)
        elif self.units == other.units:
            return self.__class__(self.value + self._scale(other))
        raise TypeError() #figure out good error message
    
    def __neg__(self):
        return self.__class__(-self.value)
    
    def __sub__(self, other):
        self + (-other)
    
    def __mul__(self, other):
        if isinstance(other, BaseUnit):
            return (self.__class__ * other.__class__) *\
                (self.value * self._scale(other.value))
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
        return repr(self.value)+"*"+self.abbrev()
    
    def __reduce__(self):
        return unit_unpickler, (self.value,
                                self.__class__.__name__,
                                self.__class__.__bases__,
                                dict(self.__class__.__dict__))
    
    __array_priority__ = 10.0 #for numpy compatibility -- ensure [1,2]*m not [1*m, 2*m]

class Derived(BaseUnit):
    def __repr__(self):
        return repr(self.value)+self.abbrev()

class Unitless(Derived):
    units = {}
    
    def __new__(cls, value):
        return value * cls.scale #Unitless things get unwrapped

UnitMeta._unit_type_reg[frozenset([])] = Unitless
UnitMeta.BaseUnit = BaseUnit

scales = (
    ("peta" , "P", Decimal_Float('1e15' )),
    ("tera" , "T", Decimal_Float('1e12' )),
    ("giga" , "G", Decimal_Float('1e9'  )),
    ("mega" , "M", Decimal_Float('1e6'  )),
    ("kilo" , "k", Decimal_Float('1e3'  )),
    ("centi", "c", Decimal_Float('1e2'  )),
    ("milli", "m", Decimal_Float('1e-3' )),
    ("micro", "u", Decimal_Float('1e-6' )),
    ("nano" , "n", Decimal_Float('1e-9' )),
    ("pico" , "p", Decimal_Float('1e-12')),
    ("femto", "f", Decimal_Float('1e-15')),
    )

def scale_unit(unit):
    for name, abbr, scale in scales:
        newunit = UnitMeta(
            name+unit.__name__,
            (Derived,),
            {
                "scale": scale*unit.scale,
                "units": unit.units,
                "abbreviation": abbr+unit.abbreviation
            }
        )
        globals()[newunit.__name__] = newunit
        globals()[newunit.abbreviation] = newunit

class meter   (BaseUnit): abbreviation = "m"
class second  (BaseUnit): abbreviation = "s"
class gram    (BaseUnit): abbreviation = "g"
class ampere  (BaseUnit): abbreviation = "A"
class mole    (BaseUnit): abbreviation = "mol"
class kelvin  (BaseUnit): abbreviation = "K" 
class candela (BaseUnit): abbreviation = "cd"
m = meter; s = second; g = gram; A = ampere; mol = mole
K = kelvin; cd = candela

for u in UnitMeta._unit_type_reg.values():
    if hasattr(u, "abbreviation"):
        scale_unit(u)

newton = kg * m / s**2; newton.__name__ = "newton"; newton.abbreviation = "N"
N = newton
joule   = N * m    ; joule  .__name__ = "joule"   ; joule  .abbreviation = "J"
J = joule
watt    = J / s    ; watt   .__name__ = "watt"    ; watt   .abbreviation = "W"
W = watt
coloumb = A * s    ; coloumb.__name__ = "coloumb" ; coloumb.abbreviation = "C"
C = coloumb
hertz = s**-1      ; hertz  .__name__ = "hertz"   ; hertz  .abbreviation = "Hz"
Hz = hertz
pascal = N / m**2  ; pascal .__name__ = "pascal"  ; pascal .abbreviation = "Pa"
Pa = pascal
volt = J / C       ; volt   .__name__ = "volt"    ; volt   .abbreviation = "V"
V = volt
ohm = V / A        ; ohm    .__name__ = "ohm"     ; ohm    .abbreviation = u"\u03A9"
O = ohm
farad = C / V      ; farad  .__name__ = "farad"   ; farad  .abbreviation = "F"
F = farad
#conductance
siemens = O**-1    ; siemens.__name__ = "siemens" ; siemens.abbreviation = "S"
S = siemens
#magnetic flux
weber = J / A      ; weber  .__name__ = "weber"   ; weber  .abbreviation = "Wb"
Wb = weber
tesla = Wb / m**2  ; tesla  .__name__ = "tesla"   ; tesla  .abbreviation = "T"
T = tesla
henry = V * s / A  ; henry  .__name__ = "henry"   ; henry  .abbreviation = "H"
H = henry
#luminous flux
lumen = cd * m**-1 ; lumen  .__name__ = "lumen"   ; lumen  .abbreviation = "lm"
lm = lumen
#illuminance
lux = lm / m**2    ; lux    .__name__ = "lux"     ; lux    .abbreviation = "lx"
lx = lux
#catalytic activity
katal = mol / s    ; katal  .__name__ = "katal"   ; katal  .abbreviation = "kat"
kat = katal
    

class minute(Derived):
    units = {second: 1}
    scale = Decimal_Float(60)
    
def scaled_unit(name, abbr, base_unit, scale_factor):
    return UnitMeta(
        name,
        (Derived,),
        {
            "abbreviation" : abbr,
            "units" : base_unit.units,
            "scale" : base_unit.scale * Decimal_Float(scale_factor)
        })

liter    = scaled_unit("liter", "L", cm**3, Decimal_Float("1000"))

inch     = scaled_unit("inches", "_in", cm, Decimal_Float("2.54"))

feet     = scaled_unit("feet", "ft", inch, Decimal_Float("12"))

hour     = scaled_unit("hour", "h", minute, Decimal_Float("60"))

angstrom = scaled_unit("meter", "ang", m, Decimal_Float("1e-10"))

mile     = scaled_unit("mile", "mile", feet, Decimal_Float("5280"))