import libtcodpy as libtcod
import cfg
import GameState

from Object import Object
from Rect import Rect
#from Fighter import Fighter
#from Item import Item
#from Equipment import Equipment
from Lights import LightValue, LightSource

import GameFlow
#import MonsterAIs

class Dungeon:
    floors = []

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None, NaturalLight = LightValue(0,0,0,0)):
        self.blocked = blocked
        self.NaturalLight = NaturalLight

        #all tiles start unexplored
        self.explored = False

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Floor:
    Tiles = []
    def __init__(self):
        return


    def create_room(self,room):
        #go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.Tiles[x][y].blocked = False
                self.Tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        #horizontal tunnel. min() and max() are used in case x1>x2
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.Tiles[x][y].blocked = False
            self.Tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        global map
        #vertical tunnel
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.Tiles[x][y].blocked = False
            self.Tiles[x][y].block_sight = False

    def make_map(self):

        #the list of objects with just the player
        GameState.objects = [GameState.player]

        #fill map with "blocked" tiles
        self.Tiles = [[ Tile(True)
                 for y in range(cfg.MAP_WIDTH) ]
               for x in range(cfg.MAP_WIDTH) ]

        rooms = []
        num_rooms = 0

        for r in range(cfg.MAX_ROOMS):
            #random width and height
            w = libtcod.random_get_int(0, cfg.ROOM_MIN_SIZE, cfg.ROOM_MAX_SIZE)
            h = libtcod.random_get_int(0, cfg.ROOM_MIN_SIZE, cfg.ROOM_MAX_SIZE)
            #random position without going out of the boundaries of the map
            x = libtcod.random_get_int(0, 0, cfg.MAP_WIDTH - w - 1)
            y = libtcod.random_get_int(0, 0, cfg.MAP_HEIGHT - h - 1)

            #"Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            #run through the other rooms and see if they intersect with this one
            failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                #this means there are no intersections, so this room is valid

                #"paint" it to the map's tiles
                self.create_room(new_room)

                #add some contents to this room, such as monsters
                self.place_objects(new_room)

                #center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    #this is the first room, where the player starts at
                    GameState.player.x = new_x
                    GameState.player.y = new_y
                    GameState.player.floor = self
                else:
                    #all rooms after the first:
                    #connect it to the previous room with a tunnel

                    #center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms-1].center()

                    #draw a coin (random number that is either 0 or 1)
                    if libtcod.random_get_int(0, 0, 1) == 1:
                        #first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        #first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                #finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

        #create stairs at the center of the last room
        GameState.stairs = Object(new_x, new_y, self, '<', 'stairs', libtcod.white, always_visible=True)
        GameState.objects.append(GameState.stairs)
        GameState.stairs.send_to_back()  #so it's drawn below the monsters

    def random_choice_index(self, chances):  #choose one option from list of chances, returning its index
        #the dice will land on some number between 1 and the sum of the chances
        dice = libtcod.random_get_int(0, 1, sum(chances))

        #go through all chances, keeping the sum so far
        running_sum = 0
        choice = 0
        for w in chances:
            running_sum += w

            #see if the dice landed in the part that corresponds to this choice
            if dice <= running_sum:
                return choice
            choice += 1

    def random_choice(self, chances_dict):
        #choose one option from dictionary of chances, returning its key
        chances = chances_dict.values()
        strings = chances_dict.keys()

        return strings[self.random_choice_index(chances)]

    def from_dungeon_level(self,table):
        #returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
        for (value, level) in reversed(table):
            if True:#GameState.dungeon_level >= level:
                return value
        return 0

    def place_objects(self,room):
        #this is where we decide the chance of each monster or item appearing.

        #maximum number of monsters per room
        max_monsters = self.from_dungeon_level([[2, 1], [3, 4], [5, 6]])

        #chance of each monster
        monster_chances = {}
        monster_chances['orc'] = 80  #orc always shows up, even if all other monsters have 0 chance
        monster_chances['troll'] = self.from_dungeon_level([[15, 3], [30, 5], [60, 7]])

        #maximum number of items per room
        max_items = self.from_dungeon_level([[1, 1], [2, 4]])

        #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
        item_chances = {}
        item_chances['heal'] = 35  #healing potion always shows up, even if all other items have 0 chance
        item_chances['lightning'] = self.from_dungeon_level([[25, 4]])
        item_chances['fireball'] =  self.from_dungeon_level([[25, 6]])
        item_chances['confuse'] =   self.from_dungeon_level([[10, 2]])
        item_chances['sword'] =     self.from_dungeon_level([[5, 4]])
        item_chances['shield'] =    self.from_dungeon_level([[15, 8]])


        #choose random number of monsters
        num_monsters = libtcod.random_get_int(0, 0, max_monsters)

        for i in range(num_monsters):
            #choose random spot for this monster
            x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
            y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

            #only place it if the tile is not blocked
            if not self.is_blocked(x, y):
                choice = self.random_choice(monster_chances)
                if choice == 'orc':
                    #create an orc
                    #TODO: Make Fighter Component
                    fighter_component = None#(hp=20, defense=0, power=4, xp=35, death_function= GameFlow.monster_death)
                    #TODO: Make Monster AIs
                    ai_component = None#MonsterAIs.BasicMonster()

                    monster = Object(x, y, self, 'o', 'orc', libtcod.desaturated_green,
                                     blocks=True, fighter=fighter_component, ai=ai_component)

                elif choice == 'troll':
                    #create a troll
                    fighter_component = None# Fighter(hp=30, defense=2, power=8, xp=100, death_function= GameFlow.monster_death)
                    ai_component = None #MonsterAIs.BasicMonster()

                    monster = Object(x, y, self, 'T', 'troll', libtcod.darker_green,
                                     blocks=True, fighter=fighter_component, ai=ai_component)

                GameState.objects.append(monster)

        #choose random number of items
        num_items = libtcod.random_get_int(0, 0, max_items)

        for i in range(num_items):
            #choose random spot for this item
            x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
            y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

            #only place it if the tile is not blocked
            if not self.is_blocked(x, y):
                choice = self.random_choice(item_chances)
                if choice == 'heal':
                    #create a healing potion
                    #TODO: Make Item Component
                    item_component = None# (use_function=None)
                    item = Object(x, y, self, '!', 'healing potion', libtcod.violet, item=item_component)

                elif choice == 'lightning':
                    #create a lightning bolt scroll
                    #TODO: Make Item Component
                    item_component = None# (use_function=None)
                    item = Object(x, y, self, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)

                elif choice == 'fireball':
                    #create a fireball scroll
                    #TODO: Make Item Component
                    item_component = None# (use_function=None)
                    item = Object(x, y, self, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)

                elif choice == 'confuse':
                    #create a confuse scroll
                    #TODO: Make Item Component
                    item_component = None# (use_function=None)
                    item = Object(x, y, self, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)

                elif choice == 'sword':
                    #create a sword
                    #TODO: Make Item Component
                    equipment_component = None
                    item = Object(x, y, self, '/', 'sword', libtcod.sky, equipment=equipment_component)

                elif choice == 'shield':
                    #create a shield
                    #TODO: Make Item Component
                    equipment_component = None
                    item = Object(x, y, self, '[', 'shield', libtcod.darker_orange, equipment=equipment_component)

                GameState.objects.append(item)
                item.send_to_back()  #items appear below other objects
                item.always_visible = True  #items are visible even out-of-FOV, if in an explored area

    def is_blocked(self,x, y):
        #first test the map tile
        if self.Tiles[x][y].blocked:
            return True

        #now check for any blocking objects
        for object in GameState.objects:
            if object.blocks and object.x == x and object.y == y and object.floor == self:
                return True

        return False