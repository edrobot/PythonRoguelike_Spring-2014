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

import BodyParts, Resistance

##class PartNames:
##    #Common part names
##    PART_TORSO = "Torso"
##    PART_HAND = "Hand"
##    PART_RING_FINGER = "Ring Finger"
##    PART_BACK = "Back"
##    PART_LEGS = "Legs" #This is for a pair of legs. Quadrupeds have more than one set of legs.
##    PART_HEAD = "Head"
##    PART_FEET = "Feet"

##class ResistanceNames:
##    #Common Resistance Names
##    RESISTANCE_NONMAGICAL = "Nonmagical"
##    RESISTANCE_MAGICAL = "Magical"
##
##class ResistanceMismatchException(Exception):
##    pass

class NotAnItemException(Exception):
    pass

class StatisticScaleingRanks:
    _S = 3
    _A = 2
    _B = 1
    _C = 0
    _D = -1
    _E = -2
    _F = -3
    _X = -4

    _offset = 4

    _rank = {0.00, 0.50, 0.75, 0.85, 1.00, 1.25, 1.50, 2.00}

    def Get_Rank(self, rank):
        if(rank + _offset > len(_offset)):
            return _rank[len(_offset) - 1]
        elif rank + _offset < 0:
            return _rank[0]
        else:
            return _rank[rank+_offset]

class Torch:
    pass

class Equipment:
    self.slot = None

class Weapon (Equipment):
    self.slot = BodyParts.Hand()
    baseAttack = 25
    baseDamage = 5

class Armor (Equipment):
    self.slot = BodyParts.Torso()
    baseDefense = 25

