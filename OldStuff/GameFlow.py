import libtcodpy as libtcod
import math
import textwrap
import shelve

import GameFlow

import GUI
import Map

import cfg
import GameState

from Entity import Entity
from Object import Object
from Item import Item
from Map import Tile
from Equipment import Equipment


def handle_keys():
    global key

    if GameState.key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif GameState.key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game

    if game_state == 'playing':
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
        elif GameState.key.vk == libtcod.KEY_KP5:
            pass  #do nothing ie wait for the monster to come to you
        else:
            #test for other keys
            key_char = chr(GameState.key.c)

            if key_char == 'g':
                #pick up an item
                for object in GameState.objects:  #look for an item in the player's tile
                    if object.x == player.x and object.y == player.y and object.item:
                        GameState.player.Pick_Up(object)
                        break

            if key_char == 'i':
                #show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'd':
                #show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
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

    #try to find an attackable object there
    target = None
    for object in GameState.objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    #attack if target found, move otherwise
    if target is not None:
        GameState.player.fighter.attack(target)
    else:
        GameState.player.move(dx, dy)
        GameState.fov_recompute = True

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
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()

        (x, y) = (GameState.mouse.cx, GameState.mouse.cy)

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape

        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
                (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)

def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None

        #return the first clicked monster, otherwise continue looping
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj

def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def save_game():
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = map
    file['objects'] = objects
    file['player_index'] = objects.index(player)  #index of player in objects list
    file['stairs_index'] = objects.index(stairs)  #same for the stairs
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['dungeon_level'] = dungeon_level
    file.close()

def load_game():
    #open the previously saved shelve and load the game data
    global map, objects, player, stairs, inventory, game_msgs, game_state, dungeon_level

    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]  #get index of player in objects list and access it
    stairs = objects[file['stairs_index']]  #same for the stairs
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    dungeon_level = file['dungeon_level']
    file.close()

    initialize_fov()

def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level

    #create object representing the player
    entity_component = Entity(5)
    GameState.player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, entity=entity_component)

    GameState.player.level = 1

    #generate map (at this point it's not drawn to the screen)
    dungeon_level = 1
    Map.make_map()
    initialize_fov()

    game_state = 'playing'
    GameState.inventory = []

    #create the list of game messages and their colors, starts empty
    GameState.game_msgs = []

    #a warm welcoming message!
    GUI.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.red)

    #initial equipment: a dagger
    equipment_component = Equipment(slot='right hand', power_bonus=2)
    obj = Object(0, 0, '-', 'dagger', libtcod.sky, equipment=equipment_component)
    GameState.inventory.append(obj)
    equipment_component.equip()
    obj.always_visible = True

def next_level():
    #advance to the next level
    global dungeon_level
    message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    player.fighter.heal(player.fighter.max_hp / 2)  #heal the player by 50%

    dungeon_level += 1
    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
    make_map()  #create a fresh new level!
    initialize_fov()

def initialize_fov():
    GameState.fov_recompute = True

    #create the FOV map, according to the generated map
    GameState.fov_map = libtcod.map_new(cfg.MAP_WIDTH, cfg.MAP_HEIGHT)
    for y in range(cfg.MAP_HEIGHT):
        for x in range(cfg.MAP_WIDTH):
            libtcod.map_set_properties(GameState.fov_map, x, y, not GameState.map[x][y].block_sight, not GameState.map[x][y].blocked)

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
        check_level_up()

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
            for object in objects:
                if object.ai:
                    object.ai.take_turn()

def main_menu():
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, cfg.SCREEN_WIDTH/2, cfg.SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER,
                                 'TOMBS OF THE ANCIENT KINGS')
        libtcod.console_print_ex(0, cfg.SCREEN_WIDTH/2, cfg.SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Jotaf')

        #show options and wait for the player's choice
        choice = GUI.menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

        if choice == 0:  #new game
            new_game()
            play_game()
        if choice == 1:  #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:  #quit
            break

