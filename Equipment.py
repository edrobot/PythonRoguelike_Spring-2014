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

import BodyParts, Resistance, GUI

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

class StatisticScaleingRank:
    _S = 3
    _A = 2
    _B = 1
    _C = 0
    _D = -1
    _E = -2
    _F = -3
    _X = -4

    _offset = 4

    _rank = (0.00, 0.50, 0.75, 0.85, 1.00, 1.25, 1.50, 2.00)

    @staticmethod
    def Get_Rank(rank = 0):
        if(rank + StatisticScaleingRank._offset > len(StatisticScaleingRank._rank)):
            return StatisticScaleingRank._rank[len(StatisticScaleingRank._offset) - 1]
        elif rank + StatisticScaleingRank._offset < 0:
            return StatisticScaleingRank._rank[0]
        else:
            return StatisticScaleingRank._rank[rank+StatisticScaleingRank._offset]

class Torch:
    pass

class Equipment:
    slot = None
    currentEquipptedPart = None
    owner = None
    is_equipped = False

    def equip(self, equipPart = None):
        if (equipPart != None):
            if (isinstance(equipPart, self.slot) and equipPart.currentItem == None):
                equipPart.currentItem = self
                self.currentEquipptedPart = equipPart
                self.is_equipped = True
                GUI.message("You equippted something!")
                return True
            return False
        else:
            x = BodyParts.Part()

            for x in self.owner.owner.parts:
                if isinstance(x, BodyParts.Part):
                    if (isinstance(x, self.slot) and x.currentItem == None):
                        return self.equip(x)
            return False


    def unequip(self):
        if(self.currentEquipptedPart != None):
            self.currentEquipptedPart.currentItem = None
            self.currentEquipptedPart = None
        self.is_equipped = False
        GUI.message("You unequippted something!")

    def toggle_equip(self):
        if not(self.is_equipped):

            x = BodyParts.Part()

            for x in self.owner.owner.parts:
                if (isinstance(x, self.slot) and x.currentItem == None):
                    self.equip(x)
                    return
        else:
            self.unequip()
            return


class Weapon (Equipment):
    scaling_Str = 0
    scaling_Dex = 0
    weapon_Range = 0 #It must be 1 or higher to be counted as a ranged weapon.
    def __init__(self, slot = BodyParts.Torso(), baseAttack = 25, baseDamage = 10, attackType = [],
                    scaling_Str = StatisticScaleingRank._C,
                    scaling_Dex = StatisticScaleingRank._C):
        self.slot = BodyParts.Hand
        self.attackType = attackType
        self.baseAttack = baseAttack
        self.baseDamage = baseDamage

        self.scaling_Str = scaling_Str
        self.scaling_Dex = scaling_Dex

class RangedWeapon (Equipment):
    weapon_Range = 5


class Sword (Weapon):
    pass

class Bow (RangedWeapon):
    def __init__(self):
        self.slot = BodyParts.Hand
        self.attackType = [Resistance.Piercing, Resistance.Mundane]
        self.baseAttack = 25
        self.baseDamage = 10
        self.scaling_Str = StatisticScaleingRank._C
        self.scaling_Dex = StatisticScaleingRank._B
        self.weapon_Range = 5

class DragonSword(Sword):
    def __init__(self):
        self.slot = BodyParts.Hand
        self.attackType = [Resistance.Slashing, Resistance.Mundane]
        self.baseAttack = 25
        self.baseDamage = 10
        self.scaling_Str = StatisticScaleingRank._C
        self.scaling_Dex = StatisticScaleingRank._C
        self.weapon_Range = 0


class Armor (Equipment):
    slot = BodyParts.Part()
    deflections = []
    resistances = []
    baseDefense = 0

    def __init__(self, slot = BodyParts.Torso(), baseDefense = 25, deflections = [], resistances = []):
        self.slot = slot
        self.deflections = deflections
        self.resistances = resistances
        self.baseDefense = baseDefense

    def hasResistance(self,target):
        res = resistances.count(target)
        if(res > 0):
            return True
        else:
            return False

    def hasDeflection(self,target):
        defl = deflections.count(target)
        if(defl > 0):
            return True
        else:
            return False



class HeavyArmor (Armor):
    pass

class PlateMail(Armor):
    def __init__(self):
        self.slot = BodyParts.Torso
        self.deflections = []
        self.resistances = [Resistance.Slashing()]
        self.baseDefense = 0

class LightArmor (Armor):
    pass

class Shield (Armor):
    pass