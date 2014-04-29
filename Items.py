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
import cfg
import GameState
import GUI

class Item():
    use_function = None
    owner = None
    def __init__(self, use_function = None):
        self.use_function = use_function

    def drop(self):
        pass

    def use(self):
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return
        if(self.use_function != None):
            self.use_function()
        else:
            GUI.message("That doesn't do anything (yet)")

