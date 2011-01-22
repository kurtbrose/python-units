import traceback

import units

def base_unit_test():
    assert 1*units.m   == 1*units.meter
    assert 1*units.s   == 1*units.second
    assert 1*units.g   == 1*units.gram
    assert 1*units.A   == 1*units.ampere
    assert 1*units.mol == 1*units.mole
    assert 1*units.K   == 1*units.kelvin
    assert 1*units.cd  == 1*units.candela
    
def base_unit_neg_test():
    assert 1*units.m   != 1*units.s
    assert 1*units.m   != 1*units.g
    assert 1*units.m   != 1*units.A
    assert 1*units.m   != 1*units.mol
    assert 1*units.m   != 1*units.K
    assert 1*units.m   != 1*units.cd
    
    assert 1*units.s   != 1*units.g
    assert 1*units.s   != 1*units.A
    assert 1*units.s   != 1*units.mol
    assert 1*units.s   != 1*units.K
    assert 1*units.s   != 1*units.cd
    
    assert 1*units.g   != 1*units.A
    assert 1*units.g   != 1*units.mol
    assert 1*units.g   != 1*units.K
    assert 1*units.g   != 1*units.cd
    
    assert 1*units.A   != 1*units.mol
    assert 1*units.A   != 1*units.K
    assert 1*units.A   != 1*units.cd
    
    assert 1*units.mol != 1*units.K
    assert 1*units.mol != 1*units.cd
    
    assert 1*units.K   != 1*units.cd

def newton_test():
    assert 1*units.N   == 1*units.newton
    assert 1*units.N   == 1*(units.kg * units.m / units.s)

def joule_test():
    assert 1*units.J   == 1*units.joule
    assert 1*units.J   == 1*(units.N * units.m)
    assert 1*units.J   == 1*(units.kg * units.m**2 / units.s)
    
def watt_test():
    assert 1*units.W   == 1*units.watt
    assert 1*units.W   == 1*(units.J / units.s)
    assert 1*units.W   == 1*(units.kg * units.m**2 / units.s**2)
    
def coloumb_test():
    assert 1*units.C   == 1*units.coloumb
    assert 1*units.C   == 1*(units.A * units.s)

def hertz_test():
    assert 1*units.Hz  == 1*units.hertz
    assert 1*units.Hz  == 1*(units.s**-1)
    
def pascal_test():
    assert 1*units.Pa  == 1*units.pascal
    assert 1*units.Pa  == 1*(units.N / units.meter**2)
    assert 1*units.Pa  == 1*(units.kg / (units.m * units.s))
    
def volt_test():
    assert 1*units.V   == 1*units.volt
    assert 1*units.V   == 1*(units.J / units.C)
    assert 1*units.V   == 1*(units.kg * units.m**2 / (units.s**2 * units.A))

def ohm_test():
    assert 1*units.O   == 1*units.ohm
    assert 1*units.O   == 1*(units.volt / units.amper)
    assert 1*units.O   == 1*(units.kg * units.m**2 / (units.s**2 * units.A))

def farad_test():
    assert 1*units.F   == 1*units.farad
    assert 1*units.F   == 1*(units.C / units.V)
    assert 1*units.F   == 1*(units.A**2 * units.s**3 / (units.kg * units.m**2))

def siemens_test():
    assert 1*units.S   == 1*units.siemens
    assert 1*units.S   == 1*(units.O**-1)
    assert 1*units.S   == 1*(units.s**2 * units.A / (units.kg * units.m**2))

def weber_test():
    assert 1*units.Wb  == 1*units.weber
    assert 1*units.Wb  == 1*(units.J / units.A)
    assert 1*units.Wb  == 1*(units.kg * units.m**2 / (units.s * units.A))
    
def tesla_test():
    assert 1*units.T   == 1*units.tesla
    assert 1*units.T   == 1*(units.Wb / units.m**2)
    assert 1*units.T   == 1*(units.kg / (units.s * units.A))
    
def henry_test():
    assert 1*units.H   == 1*units.henry
    assert 1*units.H   == 1*(units.V * units.s / units.A)
    assert 1*units.H   == 1*(units.kg * units.m**2 / (units.s * units.A**2))

def lumen_test():
    assert 1*units.lm  == 1*units.lumen
    assert 1*units.lm  == 1*(units.cd / units.m)

def lux_test():
    assert 1*units.lx  == 1*units.lux
    assert 1*units.lx  == 1*(units.lm / units.m**2)
    assert 1*units.lx  == 1*(units.cd / units.m**3)
    
def katal_test():
    assert 1*units.kat == 1*units.katal
    assert 1*units.kat == 1*(units.mol / units.s)
    
def minute_test():
    assert 1*units.minute == 60*units.s
    
def liter_test():
    assert 1*units.liter == 1000*units.cm**3
    assert 1*units.liter == 1*units.L

def inch_test():
    assert 1*units.inch == 2.54*units.cm
    assert 1*units.inch == 1*units._in
    
def feet_test():
    assert 1*units.feet == 12*units.inch
    assert 1*units.feet == 1*units.ft
    
def hour_test():
    assert 1*units.hour == 60*units.minute
    assert 1*units.hour == 3600*units.s
    assert 1*units.hour == 1*units.h
    
def angstrom_test():
    assert 1*units.angstrom == 10^-10*units.m
    assert 1*units.angstrom == 1*units.ang
    
def mile_test():
    assert 1*units.mile == 5280*units.feet

def scale_test():
    assert 1*units.Pg == 10**15  * units.g
    assert 1*units.Tg == 10**12  * units.g
    assert 1*units.Gg == 10**9   * units.g
    assert 1*units.Mg == 10**6   * units.g
    assert 1*units.kg == 10**3   * units.g
    assert 1*units.cg == 10**-2  * units.g
    assert 1*units.mg == 10**-3  * units.g
    assert 1*units.ug == 10**-6  * units.g
    assert 1*units.ng == 10**-9  * units.g
    assert 1*units.pg == 10**-12 * units.g
    assert 1*units.fg == 10**-15 * units.g
    
def add_test():
    assert 1*units.m + 1*units.m == 2*units.m
    
def subtraction_test():
    assert 2*units.m - 1*units.m == 1*units.m

def multiply_test():
    assert 1*units.m * 1*units.m == 1*umits.m**2

def division_test():
    assert 1*units.m**2 / 1*units.m == 1*units.m

def power_test():
    assert (2*units.m)**3 == 8*units.m**3

def main():
    for test in [add_test,]:
        try:
            test()
        except AssertionError:
            print "test", test.__name__, "failed:"
            traceback.print_exc()
