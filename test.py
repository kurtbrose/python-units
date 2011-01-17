import traceback

import units



def add_test():
    assert 1*units.m + 1*units.m == 2*units.m




def main():
    for test in [add_test,]:
        try:
            test()
        except AssertionError:
            print "test", test.__name__, "failed:"
            traceback.print_exc()
