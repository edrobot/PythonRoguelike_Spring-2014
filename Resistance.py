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

"""

Most "pure element" Entities have a weakness based on the Wu Xing, the five
classical elements of chinese philosophy.

Overcoming:
    Wood parts earth,
    Earth dams water,
    Water extinguishes fire
    Fire melts Metal,
    Water nourishes Wood,

Generating Tree:
    Wood feeds Fire,
    Fire hardens Earth*,
    Earth bears Metal,
    Metal Enriches Water,
    Water Nourishes Wood,

*should be "creates earth", but I feel the metaphor works better
when compared clay being heated by a furance.

A couple other resistances to note:
    Cold and Fire are weak to each other.
    Light and Dark are weak to each other.
    Dragons are weak to Cold and Dragon.
    Cold Iron is strong against Magic, but weak against Mundane.
    Void is weak to Void, but void Entitys tend to have lots of other resistances.


"""
class ResistanceScaleingRanks:
    _S = 3
    _A = 2
    _B = 1
    _C = 0
    _D = -1
    _E = -2
    _F = -3

    _offset = 3

    _rank = {4.00, 2.00, 1.50, 1.00, 0.50, 0.00, -1.00}

    @staticmethod
    def Get_Rank(rank = 0):
        if(rank + ResistanceScaleingRanks._offset > len(ResistanceScaleingRanks._offset)):
            return ResistanceScaleingRanks._rank[len(ResistanceScaleingRanks._offset) - 1]
        elif rank + ResistanceScaleingRanks._offset < 0:
            return ResistanceScaleingRanks._rank[0]
        else:
            return ResistanceScaleingRanks._rank[rank+ResistanceScaleingRanks._offset]

class Resistance:
    rank = ResistanceScaleingRanks._C

    def __init__(self, rank = 1):
        self.rank = rank

    def __add__(a,b):
        return(Resistance(a.name,a.rank + b.rank))

class Magic (Resistance):
    pass

class Mundane (Resistance):
    pass

class Blunt (Resistance):
    pass

class Piercing (Resistance):
    pass

class Slashing (Resistance):
    pass

class Holy (Resistance):
    pass

class Dark (Resistance):
    pass

class Cold (Resistance):
    pass

#Wu Xing Elements

class Fire (Resistance):
    pass

class Metal (Resistance):
    pass

class Magic (Resistance):
    pass

class Wood (Resistance):
    pass

class Water (Resistance):
    pass


