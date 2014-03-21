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
    def __init__(self, use_function):
        self.use_function = use_function

    def drop():
        pass

