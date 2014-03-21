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

class Part:
    name = "GenericPart"
    currentItem = None

    def __init__(self,name = None):
        if(name != None):
           self.name = name

class Hand(Part):
    name = "Hand"
    currentItem = None

class Legs(Part):
    name = "Legs"
    currentItem = None

class Feet(Part):
    name = "Feet"
    currentItem = None

class Torso(Part):
    name = "Torso"
    currentItem = None

class Head(Part):
    name = "Head"
    currentItem = None