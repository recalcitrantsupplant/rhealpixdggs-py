r"""
This Python 3.3 module implements several helper functions for coding map projections.

CHANGELOG:

- Alexander Raichev (AR), 2012-01-26: Refactored code from release 0.3.
- AR, 2013-07-23: Ported to Python 3.3.

NOTE:

All lengths are measured in meters and all angles are measured in radians 
unless indicated otherwise. 
"""
#*****************************************************************************
#       Copyright (C) 2012 Alexander Raichev <alex.raichev@gmail.com>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

# Import third-party modules.
from numpy import pi, floor, sqrt, log, sin, arcsin, deg2rad, rad2deg, sign 

def wrap_longitude(lam, radians=False):
    r"""
    Given a point p on the unit circle at angle `lam` from the positive 
    x-axis, return its angle theta in the range -pi <= theta < pi.
    If `radians` = True, then `lam` and the output are given in radians.
    Otherwise, they are given in degrees.
    
    EXAMPLES::
    
        >>> wrap_longitude(2*pi + pi, radians=True)
        -3.1415926535897931
        >>> wrap_longitude(-185, radians=False)
        175.0
        >>> wrap_longitude(-180, radians=False)
        -180.0
        >>> wrap_longitude(185, radians=False)
        -175.0

    """
    if not radians:
        # Convert to radians.
        lam = deg2rad(lam)
    if lam < -pi or lam >= pi:
        result = lam - 2*pi*floor(lam/(2*pi))    # x mod 2*pi
        if result >= pi:
            result = result - 2*pi
    else:
        result = lam
    if not radians:
        # Convert to degrees.
        result = rad2deg(result)
    return result
        
def wrap_latitude(phi, radians=False):
    r"""
    Given a point p on the unit circle at angle `phi` from the positive x-axis,
    if p lies in the right half of the circle, then return its angle that lies 
    in the interval [-pi/2, pi/2].
    If p lies in the left half of the circle, then reflect it through the 
    origin, and return the angle of the reflected point that lies in the 
    interval [-pi/2, pi/2].
    If `radians` = True, then `phi` and the output are given in radians.
    Otherwise, they are given in degrees.
    
    EXAMPLES::

        >>> wrap_latitude(45, radians=False)
        45.0
        >>> wrap_latitude(-45, radians=False)
        -45.0
        >>> wrap_latitude(90, radians=False)
        90.0
        >>> wrap_latitude(-90, radians=False)
        -90.0
        >>> wrap_latitude(135, radians=False)
        -45.0
        >>> wrap_latitude(-135, radians=False)
        45.0

    """
    if not radians:
        # Convert to radians.
        phi = deg2rad(phi)
    # Put phi in range -pi <= phi < pi.
    phi = wrap_longitude(phi, radians=True)
    if abs(phi) <= pi/2:
        result = phi
    else:
        result = phi - sign(phi)*pi
    if not radians:
        # Convert to degrees.
        result = rad2deg(result)
    return result
    
def auth_lat(phi, e, inverse=False, radians=False):
    r"""
    Given a point of geographic latitude `phi` on an ellipse of 
    eccentricity `e`, return the authalic latitude of the point.
    If `inverse` =True, then compute its inverse approximately.
    
    EXAMPLES::
    
        >>> beta = auth_lat(pi/4, 0.5, radians=True); beta
        0.68951821243544043
        >>> auth_lat(beta, 0.5, radians=True, inverse=True); pi/4
        0.78512652358127166
        0.7853981633974483
        
    NOTES:
    
    The power series approximation used for the inverse is
    standard in cartography (PROJ.4 uses it, for instance)
    and accurate for small eccentricities.
    """
    if e == 0:
        return phi
    if not radians:
        # Convert to radians to do calculations below.
        phi = deg2rad(phi)
    if not inverse:
        # Compute authalic latitude from latitude phi.
        q = ((1 - e**2)*sin(phi))/(1 - (e*sin(phi))**2) - \
            (1 - e**2)/(2.0*e)*log((1 - e*sin(phi))/(1 + e*sin(phi)))
        qp = 1 - (1 - e**2)/(2.0*e)*log((1.0 - e)/(1.0 + e))
        ratio = q/qp
        # Avoid rounding errors.
        if abs(ratio) > 1:
            # Make abs(ratio) = 1
            ratio = sign(ratio) 
        result = arcsin(ratio)
    else:
        # Compute an approximation of latitude from authalic latitude phi.
        result = phi +\
                 (e**2/3.0 + 31*e**4/180.0 + 517*e**6/5040.0)*sin(2*phi) +\
                 (23*e**4/360.0 + 251*e**6/3780.0)*sin(4*phi) +\
                 (761*e**6/45360.0)*sin(6*phi)
    if not radians:
        # Convert back to degrees.
        result = rad2deg(result)
    return result
    
def auth_rad(a, e, inverse=False):
    r"""
    Return the radius of the authalic sphere of the ellipsoid with major
    radius `a` and eccentricity `e`.
    If `inverse` = True, then return the major radius of the ellipsoid
    with authalic radius `a` and eccentricity `e`.
    
    EXAMPLES::
    
        >>> auth_rad(1, 0)
        1
        >>> for i in range(2, 11):
        ...     e = 1.0/i**2     
        ...     print(e, auth_rad(1, 1.0/i**2))
        0.25 0.98939325967
        0.1111111111111111 0.99793514743
        0.0625 0.999348236456
        0.04 0.999733212354
        0.027777777777777776 0.999871371052
        0.02040816326530612 0.999930576286
        0.015625 0.999959307081
        0.012345679012345678 0.999974596271
        0.01 0.999983332861

    """
    if e == 0:
        return a
    k = sqrt(0.5*(1 - (1 - e**2)/(2*e)*log((1 - e)/(1 + e))))
    if not inverse:
        # The expression below is undefined when e=0 (sphere),
        # but its limit as e tends to 0 is a, as expected.
        return a*k
    else:
        # Then a is the authalic radius and output major radius of ellipsoid.
        return a/k