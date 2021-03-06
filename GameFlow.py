import libtcodpy as libtcod
import math
import textwrap
import shelve

import GameFlow

import GUI
import Map

import cfg
import GameState

import Equipment

import BodyParts

import Lights

from Entity import Entity
from Object import Object
#from Item import Item
from Map import Tile, Dungeon, Floor
#from Equipment import Equipment


def handle_keys():
    global key

    if GameState.game_state == 'playing':
        #movement keys
        if GameState.key.vk == libtcod.KEY_UP or GameState.key.vk == libtcod.KEY_KP8:
            player_move_or_attack(0, -1)
        elif GameState.key.vk == libtcod.KEY_DOWN or GameState.key.vk == libtcod.KEY_KP2:
            player_move_or_attack(0, 1)
        elif GameState.key.vk == libtcod.KEY_LEFT or GameState.key.vk == libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)
        elif GameState.key.vk == libtcod.KEY_RIGHT or GameState.key.vk == libtcod.KEY_KP6:
            player_move_or_attack(1, 0)
        elif GameState.key.vk == libtcod.KEY_HOME or GameState.key.vk == libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)
        elif GameState.key.vk == libtcod.KEY_PAGEUP or GameState.key.vk == libtcod.KEY_KP9:
            player_move_or_attack(1, -1)
        elif GameState.key.vk == libtcod.KEY_END or GameState.key.vk == libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)
        elif GameState.key.vk == libtcod.KEY_PAGEDOWN or GameState.key.vk == libtcod.KEY_KP3:
            player_move_or_attack(1, 1)
        elif GameState.key.vk == libtcod.KEY_KP5 or GameState.key.vk == '.':
            pass  #do nothing ie wait for the monster to come to you
        else:
            #test for other keys
            key_char = chr(GameState.key.c)

            if key_char == 'g':
                #pick up an item
                for object in GameState.objects:  #look for an item in the player's tile
                    if object.x == GameState.player.x and object.y == GameState.player.y and GameState.player.floor == object.floor and object.item:
                        GameState.player.entity.Pick_Up(object)
                        break

            if key_char == 'f':
                #(F)ire your weapon.
                AttackingWeapons = []
                DefendingArmor = []

                AttackingTypes = []
                DefendingResistances = []

                x = BodyParts.Part()
                y = Equipment.RangedWeapon()

                for x in GameState.player.entity.parts:
                    if (isinstance(x,BodyParts.Part)):
                        y = x.currentItem
                        if isinstance(y, Equipment.RangedWeapon):
                            AttackingWeapons.append(x.currentItem)
                if len(AttackingWeapons) > 0:
                    GUI.message("Select a target to attack.")
                    target = target_monster(AttackingWeapons[0].weapon_Range)
                    if target != None:
                        GameState.player.entity.melee_attack_entity(target.entity)
                        GameState.player.move(0, 0)
                        GameState.fov_recompute = True
                else:
                    GUI.message("Cancelled")


            if key_char == 'i':
                #show the inventory; if an item is selected, use it
                chosen_item = GUI.inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'd':
                #show the inventory; if an item is selected, drop it
                chosen_item = GUI.inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if key_char == 'c':
                #show character information
                level_up_xp = cfg.LEVEL_UP_BASE + GameState.player.level * cfg.LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(GameState.player.fighter.xp) +
                       '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(GameState.player.fighter.max_hp) +
                       '\nAttack: ' + str(GameState.player.fighter.power) + '\nDefense: ' + str(GameState.player.fighter.defense), cfg.CHARACTER_SCREEN_WIDTH)

            if key_char == '<':
                #go down stairs, if the player is on them
                if GameState.stairs.x == GameState.player.x and GameState.stairs.y == GameState.player.y:
                    next_level()

            return 'didnt-take-turn'

def player_move_or_attack(dx, dy):

    #the coordinates the player is moving to/attacking
    x = GameState.player.x + dx
    y = GameState.player.y + dy
    floor = GameState.player.floor

    #try to find an attackable object there
    target = None
    for Object in GameState.objects:
        if Object.entity and Object.x == x and Object.y == y and Object.floor == floor:
            target = Object
            GameState.player.entity.melee_attack_entity(target.entity)
            break

    GameState.player.move(dx, dy)
    GameState.fov_recompute = True

    #attack if target found, move otherwise
##    if target is not None:
##        GameState.player.fighter.attack(target)
##    else:
##        GameState.player.move(dx, dy)
##        GameState.fov_recompute = True

def check_level_up():
    #see if the player's experience is enough to level-up
    level_up_xp = cfg.LEVEL_UP_BASE + GameState.player.level * cfg.LEVEL_UP_FACTOR
    if GameState.player.fighter.xp >= level_up_xp:
        #it is! level up and ask to raise some stats
        GameState.player.level += 1
        GameState.player.fighter.xp -= level_up_xp
        message('Your battle skills grow stronger! You reached level ' + str(GameState.player.level) + '!', libtcod.yellow)

        choice = None
        while choice == None:  #keep asking until a choice is made
            choice = menu('Level up! Choose a stat to raise:\n',
                          ['Constitution (+20 HP, from ' + str(GameState.player.fighter.max_hp) + ')',
                           'Strength (+1 attack, from ' + str(GameState.player.fighter.power) + ')',
                           'Agility (+1 defense, from ' + str(GameState.player.fighter.defense) + ')'], cfg.LEVEL_SCREEN_WIDTH)

        if choice == 0:
            GameState.player.fighter.base_max_hp += 20
            GameState.player.fighter.hp += 20
        elif choice == 1:
            GameState.player.fighter.base_power += 1
        elif choice == 2:
            GameState.player.fighter.base_defense += 1

def player_death(player):
    #the game ended!
    message('You died!', libtcod.red)
    GameState.game_state = 'dead'

    #for added effect, transform the player into a corpse!
    GameState.player.char = '%'
    GameState.player.color = libtcod.dark_red

def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    message('The ' + monster.name + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points.', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()

def target_tile(max_range=None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, GameState.key, GameState.mouse)
        GUI.render_all()

        (x, y) = (GameState.mouse.cx, GameState.mouse.cy)

        if GameState.mouse.rbutton_pressed or GameState.key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape

        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (GameState.mouse.lbutton_pressed and libtcod.map_is_in_fov(GameState.fov_map, x, y) and
                (max_range is None or GameState.player.distance(x, y) <= max_range)):
            return (x, y)

def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None

        #return the first clicked monster, otherwise continue looping
        for obj in GameState.objects:
            if obj.x == x and obj.y == y and obj.entity and obj != GameState.player:
                return obj

def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(GameState.fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def save_game():
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = GameState.dungeon
    file['objects'] = GameState.objects
    file['player_index'] = GameState.objects.index(GameState.player)  #index of player in objects list
    file['stairs_index'] = GameState.objects.index(GameState.stairs)  #same for the stairs
    file['inventory'] = GameState.inventory
    file['game_msgs'] = GameState.game_msgs
    file['game_state'] = GameState.game_state
    file.close()

def load_game():
    #open the previously saved shelve and load the game data
    global map, objects, player, stairs, inventory, game_msgs, game_state, dungeon_level

    file = shelve.open('savegame', 'r')
    GameState.dungeon = file['map']
    GameState.objects = file['objects']
    GameState.player = objects[file['player_index']]  #get index of player in objects list and access it
    GameState.stairs = objects[file['stairs_index']]  #same for the stairs
    GameState.inventory = file['inventory']
    GameState.game_msgs = file['game_msgs']
    GameState.game_state = file['game_state']
    file.close()

    initialize_fov()

def new_game():

    #create object representing the player
    entity_component = Entity(9999)
    #lightComp = Lights.LightSource(255,255,0,5)
    GameState.player = Object(0, 0, None, '@', 'player', libtcod.black, blocks=True, entity = entity_component)
    GameState.player.lightSource = Lights.LightSource(255,255,0,5)
    GameState.player.level = 1

    #generate map (at this point it's not drawn to the screen)
    newDungeon = Map.Dungeon()
    newFloor = Map.Floor()

    newFloor.make_map()

    newDungeon.floors.append(newFloor)

    GameState.dungeon = newDungeon

    equipment_component = Equipment.DragonSword()
    bow_comp = Equipment.Bow()
    sword = Object(0, 0, newFloor, '/', 'Dragon Sword', libtcod.sky, equipment=equipment_component)
    bow = Object(0, 0, newFloor, '/', 'Bow', libtcod.sky, equipment=bow_comp)
    GameState.player.entity.Pick_Up(sword)
    GameState.player.entity.Pick_Up(bow)

    initialize_fov()

    GameState.game_state = 'playing'
    GameState.inventory = []

    #create the list of game messages and their colors, starts empty
    GameState.game_msgs = []
    GameState.player.floor = newFloor



##    #a warm welcoming message!
##    GUI.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.red)
##
##    #initial equipment: a dagger
##    equipment_component = Equipment(slot='right hand', power_bonus=2)
##    obj = Object(0, 0, '-', 'dagger', libtcod.sky, equipment=equipment_component)
##    GameState.inventory.append(obj)
##    equipment_component.equip()
##    obj.always_visible = True

def next_level():
    #advance to the next level
    #global dungeon_level
    GUI.message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    #TODO: Make Fighter Component
    #GameState.player.fighter.heal(player.fighter.max_hp / 2)  #heal the player by 50%

    #dungeon_level += 1
    GUI.message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)

    #GameState.dungeon.floors()  #create a fresh new level!
    newFloor = Map.Floor()
    newFloor.make_map()
    GameState.dungeon.floors.append(newFloor)
    GameState.player.floor = newFloor
    initialize_fov()

def initialize_fov():
    GameState.fov_recompute = True

    #create the FOV map, according to the generated map
    GameState.fov_map = libtcod.map_new(cfg.MAP_WIDTH, cfg.MAP_HEIGHT)
    for y in range(cfg.MAP_HEIGHT):
        for x in range(cfg.MAP_WIDTH):
            libtcod.map_set_properties(GameState.fov_map, x, y, not GameState.player.floor.Tiles[x][y].block_sight, GameState.player.floor.Tiles[x][y].blocked)


    libtcod.console_clear(cfg.con)  #unexplored areas start black (which is the default background color)

def initialize_light():
    GameState.fov_recompute = True

    #create the FOV map, according to the generated map
    GameState.fov_light_map = libtcod.map_new(cfg.MAP_WIDTH, cfg.MAP_HEIGHT)
    for y in range(cfg.MAP_HEIGHT):
        for x in range(cfg.MAP_WIDTH):
            libtcod.map_set_properties(GameState.fov_light_map, x, y, not GameState.player.floor.Tiles[x][y].block_sight, GameState.player.floor.Tiles[x][y].blocked)


    libtcod.console_clear(cfg.con)  #unexplored areas start black (which is the default background color)


def play_game():

    player_action = None

    GameState.mouse = libtcod.Mouse()
    GameState.key = libtcod.Key()
    #main loop
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, GameState.key, GameState.mouse)
        #render the screen
        GUI.render_all()

        libtcod.console_flush()

        #level up if needed
        #TODO: Add level system
        #check_level_up()

        #erase all objects at their old locations, before they move
        for object in GameState.objects:
            object.clear()

        #handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break

        #let monsters take their turn

        if GameState.game_state == 'playing' and player_action != 'didnt-take-turn':
            Obj = Object()
            for Obj in GameState.objects:
                if Obj.ai != None:
                    #print "Beginning " + str(Obj) + " Move"
                    if Obj.ai.currentState.action != None:
                        Obj.ai.currentStateAction()
                    #print str(Obj) + " Finished Action"
                    Obj.ai.checkCurrentState()
                    #print str(Obj) + " Done Checking State"

def main_menu():
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, cfg.SCREEN_WIDTH/2, cfg.SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER,
                                 'MICHAEL\'S FINAL PROJECT GAME THING')
        libtcod.console_print_ex(0, cfg.SCREEN_WIDTH/2, cfg.SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Michael')

        #show options and wait for the player's choice
        choice = GUI.menu('', ['Play a new game'], 24)

        if choice == 0:  #new game
            new_game()
            play_game()
##        if choice == 1:  #load last game
##            try:
##                load_game()
##            except:
##                GUI.msgbox('\n No saved game to load.\n', 24)
##                continue
##            play_game()
##        elif choice == 2:  #quit
##            break

