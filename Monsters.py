#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Michael
#
# Created:     24/04/2014
# Copyright:   (c) Michael 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import Entity
import Object
import Resistance
import libtcodpy as libtcod
import Lights

class Orc(Object.Object):
    def __init__(self,x,y,floor):
        entity_component = Entity.Entity(level = 5, resistances = [Resistance.Cold()])
        lightComp = Lights.LightSource(0,255,0,5)
        super(Orc,self).__init__(x, y, floor, 'o', 'radioactive orc', libtcod.desaturated_green, blocks=True, entity=entity_component, lightSource = Lights.LightSource(0,0,255,5))

class Goblin(Object.Object):
    def __init__(self,x,y,floor):
        entity_component = Entity.Entity(level = 5, resistances = [Resistance.Cold()])
        super(Goblin,self).__init__(x, y, floor, 'g', 'goblin', libtcod.desaturated_green, blocks=True, entity=entity_component)
