import libtcodpy as libtcod

#-------------------------------------------------------------------------------
# Name:        GameState
# Purpose:
#
# Author:      Michael
#
# Created:     13/03/2014
# Copyright:   (c) Michael 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

objects = []
player  = None
stairs = None
inventory = []
game_msgs = []
game_state = []
dungeon = None
fov_recompute = False
lighting_recompute = False