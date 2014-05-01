import libtcodpy as libtcod
import GameState
import cfg
import Equipment
import Lights
import Entity
import Items
import AI
import StateMachine
import math
from Items import Item
from memory_profiler import profile
import psutil


class Object(object):
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.

    lightSource = Lights.LightSource()
    ai = StateMachine.StateMachine()
    def __init__(self, x = 0, y = 0, floor = 0, char = "X", name = "BLUH", color = libtcod.Color(0,0,100), blocks=False, always_visible=False, entity=None, ai=None, item=None, equipment=None, lightSource=None):
        self.x = x
        self.y = y
        self.floor = floor
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible
        self.entity = entity
        self.inventory = []
        self.lightSource = lightSource

        self.TargetLastSeenLocation = None
        self.TargetLastSeenPath = None

        if self.entity:  #let the entity component know who owns it
            self.entity.owner = self

        self.ai = ai
        #if self.ai:  #let the AI component know who owns it
        #    self.ai.owner = self

        self.item = item
        if self.item:  #let the Item component know who owns it
            self.item.owner = self

        self.equipment = equipment
        if self.equipment:  #let the Equipment component know who owns it
            self.equipment.owner = self

            #there must be an Item component for the Equipment component to work properly
            self.item = Item() #TODO: Item Class
            self.item.owner = self

    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not self.floor.is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        else:
            return False

    def move_towards(self, target_x, target_y):
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        if distance == 0:
            return
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        return self.move(dx, dy)

    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they're in the same tile.

        GameState.objects.remove(self)
        GameState.objects.insert(0, self)

    def draw(self):
        #only show if it's visible to the player; or it's set to "always visible" and on an explored tile
        if (libtcod.map_is_in_fov(GameState.fov_map, self.x, self.y) or
                (self.always_visible and GameState.player.floor.Tiles[self.x][self.y].explored) and GameState.player.floor == self.floor):
            #set the color and then draw the character that represents this object at its position
            libtcod.console_set_default_foreground(cfg.con, self.color)
            libtcod.console_put_char(cfg.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(cfg.con, self.x, self.y, ' ', libtcod.BKGND_NONE)


    def initialize_fov(self):
        GameState.fov_recompute = True

        #create the FOV map, according to the generated map
        GameState.fov_map = libtcod.map_new(cfg.MAP_WIDTH, cfg.MAP_HEIGHT)
        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                libtcod.map_set_properties(GameState.fov_map, x, y, not GameState.player.floor.Tiles[x][y].block_sight, GameState.player.floor.Tiles[x][y].blocked)


        libtcod.console_clear(cfg.con)  #unexplored areas start black (which is the default background color)


    def Event_IsPlayerInPOV(self,InternalParam = {}):
        #libtcod.map_clear(GameState.fov_map)
        #self.initialize_fov()
        return libtcod.map_is_in_fov(GameState.fov_map, self.x, self.y)

    def Event_HasCheckedLastPlayerLocation(self,InternalParam = {}):
        pass

    def clearPath(self):
        if (self.TargetLastSeenPath != None):
            libtcod.path_delete(self.TargetLastSeenPath)
        self.TargetLastSeenPath = None

    def path_func(self,xFrom,yFrom,xTo,yTo,userData):
        #print (str(xFrom) +","+ str(yFrom) + "  " + str(xTo) + "," + str(yTo))
        if (xTo == xFrom and yTo == yFrom) or ((xFrom, yFrom) == (self.x, self.y)):
            #print ("True")
            return 1.0

        elif self.floor.is_blocked(xFrom,yFrom):
            #print ("False")
            return 0.0

        else:
            #print ("True")
            return 1.0

    def ObjectAdjacency(self, Target):
        for i in range(-1,2):
            for j in range(-1,2):
                if cfg.MAP_WIDTH > i + self.x > 0 and cfg.MAP_WIDTH > j + self.y > 0 and not (i == j == 0):
                    Blocked, obj = self.floor.is_blocked(i + self.x,j + self.y,True)
                    if(Blocked):
                        if obj == Target:
                            return True
        return False

    def Action_MoveTwoardsPlayer(self, attack = False, InternalParam = {}):
        #Adjaceny Test
        print "Adjacency Test"
        pX, pY = GameState.player.x, GameState.player.y
        dist = math.sqrt(math.pow(pX - self.x,2) + math.pow(pY - self.y,2))
        if math.fabs(pX - self.x) < 1 and math.fabs(pY - self.y) <= 1:
            self.entity.melee_attack_entity(GameState.player.entity)
            return
        #if self.ObjectAdjacency(GameState.player):
        #    self.entity.melee_attack_entity(GameState.player.entity)
        #    return
        print "Passed"
        #Pov Test
        print "POV Test"
        if(self.Event_IsPlayerInPOV()):
            self.TargetLastSeenLocation = (GameState.player.x, GameState.player.y)
            if not self.move_towards(GameState.player.x, GameState.player.y):
                self.clearPath()
                self.TargetLastSeenPath = libtcod.path_new_using_function(cfg.MAP_WIDTH,cfg.MAP_WIDTH, self.path_func,(self.x,self.y))
                libtcod.path_compute(self.TargetLastSeenPath,self.x,self.y,GameState.player.x,GameState.player.y)
            #self.TargetLastSeenPath = libtcod.path_new_using_map(GameState.fov_map)

        #Move Twoards Player
        elif self.TargetLastSeenPath and self.TargetLastSeenLocation != None:
            self.clearPath()
            self.TargetLastSeenPath = libtcod.path_new_using_function(cfg.MAP_WIDTH,cfg.MAP_WIDTH, self.path_func,(self.x,self.y))
            x, y = self.TargetLastSeenLocation
            libtcod.path_compute(self.TargetLastSeenPath,self.x,self.y,x,y)
        if self.TargetLastSeenPath != None:
            x, y = self.TargetLastSeenLocation
            if(self.x, self.y) == (x,y):
                print "Giving Up Chase"
                self.clearPath()
                self.TargetLastSeenLocation = None
                return
            x,y = libtcod.path_walk(self.TargetLastSeenPath,False)

            if x != None and y != None:
                self.move_towards(x,y)
        print "Passed"

class ObjectMemory:
    def __init__(self,original, locX = 0, locY = 0, timeOut = -1):
        self.original = original
        self.locX = locX
        self.locY = locY
        self.timeOut = timeOut

    def __eq__(self, other):
        if isinstance(other, Object):
            if self.original is other:
                return True
            else:
                return False
        elif isinstance(other, ObjectMemory):
                return self == other
        else:
            return False