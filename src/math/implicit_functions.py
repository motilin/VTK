import math

"""
Implicit functions are mathematical equations that define a surface in a 3D space.
The surface is defined by the zero set of the function, i.e., the set of points
where the function evaluates to zero. The implicit function can be defined by
a lambda function that takes three arguments x, y, z and returns the value of the
function at the given point.
"""

def SURFACE(a, b, c):
    return lambda x, y, z: x**2 / a**2 - z / c


def ELLIPSOID(a, b, c):
    return lambda x, y, z: x**2 / a**2 + y**2 / b**2 + z**2 / c**2 - 1


def CONE(a, b, c):
    return lambda x, y, z: x**2 / a**2 + y**2 / b**2 - z**2 / c**2


def ELLIPTIC_PARABOLOID(a, b, c):
    return lambda x, y, z: x**2 / a**2 + y**2 / b**2 - z / c


def HYPERBOLIC_PARABOLOID(a, b, c):
    return lambda x, y, z: x**2 / a**2 - y**2 / b**2 - z / c


def HYPERBOLID_OF_ONE_SHEET(a, b, c):
    return lambda x, y, z: x**2 / a**2 + y**2 / b**2 - z**2 / c**2 - 1


def HYPERBOLID_OF_TWO_SHEETS(a, b, c):
    return lambda x, y, z: -(x**2) / a**2 - y**2 / b**2 + z**2 / c**2 - 1


def CUSTOM(a, b, c):
    return lambda x, y, z: x**2 / a**2 + y**2 / b**2 - 1


FUNCS = {
    "Custom": CUSTOM,
    "Surface": SURFACE,
    "Ellipsoid": ELLIPSOID,
    "Cone": CONE,
    "Elliptid paraboloid": ELLIPTIC_PARABOLOID,
    "Hyperbolic paraboloid": HYPERBOLIC_PARABOLOID,
    "Hyperboloid of one sheet": HYPERBOLID_OF_ONE_SHEET,
    "Heperboloid of two sheets": HYPERBOLID_OF_TWO_SHEETS,
}
