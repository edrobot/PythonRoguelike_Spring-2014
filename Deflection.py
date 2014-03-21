#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Michael
#
# Created:     21/03/2014
# Copyright:   (c) Michael 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class DeflectionScaleingRanks:
    _S = 3
    _A = 2
    _B = 1
    _C = 0
    _D = -1
    _E = -2
    _F = -3

    _offset = 3

    _rank = {4.00, 2.00, 1.50, 1.00, 0.50, 0.00, -1.00}

    def Get_Rank(self, rank):
        if(rank + _offset > len(_offset)):
            return _rank[len(_offset) - 1]
        elif rank + _offset < 0:
            return _rank[0]
        else:
            return _rank[rank+_offset]

class Deflection:
    rank = DeflectionScaleingRanks._C

    def __init__(self, rank):
        self.rank = rank

    def __add__(a,b):
        return(Resistance(a.name,a.rank + b.rank))

class Projectile(Resistance):
    pass

class Magic(Deflection):
    pass

class Melee(Deflection):
    pass

class Slashing(Deflection):
    pass

class Piercing(Deflection):
    pass

class Blunt(Deflection):
    pass

class Metal(Deflection):
    pass