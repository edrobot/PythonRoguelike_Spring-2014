import libtcodpy as libtcod
import cfg
import GameState
import textwrap
import math
import Lights
from memory_profiler import profile
import psutil

lightsOffValue = Lights.LightValue(0,0,0,0)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(cfg.panel, back_color)
    libtcod.console_rect(cfg.panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(cfg.panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(cfg.panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #finally, some centered text with the values
    libtcod.console_set_default_foreground(cfg.panel, libtcod.white)
    libtcod.console_print_ex(cfg.panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                                 name + ': ' + str(value) + '/' + str(maximum))

def get_names_under_mouse():
    #return a string with the names of all objects under the mouse

    (x, y) = (GameState.mouse.cx, GameState.mouse.cy)

    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in GameState.objects
             if obj.x == x and obj.y == y and libtcod.map_is_in_fov(GameState.fov_map, obj.x, obj.y)]

    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()

def get_light_under_mouse():
    (x, y) = (GameState.mouse.cx, GameState.mouse.cy)
    return str(GameState.player.floor.Tiles[x][y].currentLight.Brightness)  + "," + str(GameState.player.floor.Tiles[x][y].currentLight.red)

def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    #global fov_recompute

    if GameState.lighting_recompute or GameState.fov_recompute:
        for y in range(cfg.MAP_HEIGHT):
                for x in range(cfg.MAP_WIDTH):
                    GameState.player.floor.Tiles[x][y].currentLight = lightsOffValue

        for o in GameState.objects:
            if (o.lightSource != None):
                libtcod.map_clear(GameState.fov_light_map)
                libtcod.map_compute_fov(GameState.fov_map, o.x, o.y, 0, cfg.FOV_LIGHT_WALLS, cfg.FOV_ALGO)
            else:
                continue
            for y in range(cfg.MAP_HEIGHT):
                for x in range(cfg.MAP_WIDTH):
                    visible = libtcod.map_is_in_fov(GameState.fov_map, x, y)
                    wall = GameState.player.floor.Tiles[x][y].block_sight
                    distance = math.sqrt(pow(o.x - x,2) + pow(o.y - y,2))
                    if visible:
                        #it's visible
                        if wall:
                            if distance != 0:
                                GameState.player.floor.Tiles[x][y].currentLight += o.lightSource.value / distance
                            else:
                                GameState.player.floor.Tiles[x][y].currentLight += o.lightSource.value / 1
                        else:
                            if distance != 0:
                                GameState.player.floor.Tiles[x][y].currentLight += o.lightSource.value / distance
                            else:
                                GameState.player.floor.Tiles[x][y].currentLight += o.lightSource.value / 1
                            #since it's visible, explore it
                        #GameState.player.floor.Tiles[x][y].explored = True
        GameState.lighting_recompute = False
        GameState.fov_recompute = True

    if GameState.fov_recompute:
        #recompute FOV if needed (the player moved or something)
        GameState.fov_recompute = False
        libtcod.map_compute_fov(GameState.fov_map, GameState.player.x, GameState.player.y, cfg.TORCH_RADIUS, cfg.FOV_LIGHT_WALLS, cfg.FOV_ALGO)

        #go through all tiles, and set their background color according to the FOV
        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                light = Lights.LightValue()
                visible = libtcod.map_is_in_fov(GameState.fov_map, x, y)
                wall = GameState.player.floor.Tiles[x][y].block_sight
                light = GameState.player.floor.Tiles[x][y].currentLight + GameState.player.floor.Tiles[x][y].NaturalLight
                if light.Brightness < 1:
                    visible = False
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if GameState.player.floor.Tiles[x][y].explored:
                        if wall:
                            libtcod.console_set_default_foreground(cfg.con, libtcod.Color(255,255,255))
                            libtcod.console_set_char_background(cfg.con, x, y, libtcod.Color(0,0,0), libtcod.BKGND_SET)
                            libtcod.console_set_char(cfg.con, x, y,"#")
                        else:
                            libtcod.console_set_char_background(cfg.con, x, y, libtcod.Color(0,0,0), libtcod.BKGND_SET)
                            libtcod.console_set_default_foreground(cfg.con, libtcod.Color(255,255,255))
                            libtcod.console_set_char(cfg.con, x, y,".")
                else:
                    #it's visible
                    if wall:
                        libtcod.console_set_char(cfg.con, x, y," ")
                        libtcod.console_set_char_background(cfg.con, x, y, (light/2).lightToLibtcodColor(), libtcod.BKGND_SET )
                    else:
                        libtcod.console_set_char(cfg.con, x, y," ")
                        libtcod.console_set_char_background(cfg.con, x, y, light.lightToLibtcodColor(), libtcod.BKGND_SET )
                        #since it's visible, explore it
                    if(light.Brightness >= 1):
                        GameState.player.floor.Tiles[x][y].explored = True

    #draw all objects in the list, except the player. we want it to
    #always appear over all other objects! so it's drawn later.
    for object in GameState.objects:
        if object != GameState.player:
            object.draw()
    GameState.player.draw()

    #blit the contents of "con" to the root console
    libtcod.console_blit(cfg.con, 0, 0, cfg.MAP_WIDTH, cfg.MAP_HEIGHT, 0, 0, 0)


    #prepare to render the GUI panel
    libtcod.console_set_default_background(cfg.panel, libtcod.black)
    libtcod.console_clear(cfg.panel)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in GameState.game_msgs:
        libtcod.console_set_default_foreground(cfg.panel, color)
        libtcod.console_print_ex(cfg.panel, cfg.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT,line)
        y += 1

    #show the player's stats
    #TODO: Fix HP Bar
    render_bar(1, 1, cfg.BAR_WIDTH, 'HP', GameState.player.entity.hitPoints, GameState.player.entity.maxHitPoints,
               libtcod.light_red, libtcod.darker_red)
    libtcod.console_print_ex(cfg.panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(GameState.dungeon.floors.index(GameState.player.floor)))

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(cfg.panel, libtcod.light_gray)
    #libtcod.console_print_ex(cfg.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())
    libtcod.console_print_ex(cfg.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_light_under_mouse())

    #blit the contents of "panel" to the root console
    libtcod.console_blit(cfg.panel, 0, 0, cfg.SCREEN_WIDTH, cfg.PANEL_HEIGHT, 0, 0, cfg.PANEL_Y)


def message(new_msg, color = libtcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, cfg.MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(GameState.game_msgs) == cfg.MSG_HEIGHT:
            del GameState.game_msgs[0]

        #add the new line as a tuple, with the text and the color
        GameState.game_msgs.append( (line, color) )


def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(cfg.con, 0, 0, width, cfg.SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    #blit the contents of "window" to the root console
    x = cfg.SCREEN_WIDTH/2 - width/2
    y = cfg.SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:  #(special case) Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen)

    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(GameState.player.inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in GameState.player.inventory:
            text = item.name
            #show additional information, in case it's equipped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot.name + ')'
            options.append(text)

    index = menu(header, options, cfg.INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(GameState.player.inventory) == 0: return None
    return GameState.player.inventory[index].item

def msgbox(text, width=50):
    menu(text, [], width)  #use menu() as a sort of "message box"