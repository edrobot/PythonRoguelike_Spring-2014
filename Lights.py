#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Jack
#
# Created:     14/03/2014
# Copyright:   (c) Jack 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import libtcodpy as libtcod
import math
class LightValue:
    Brightness = 0
    red = 256
    blue = 256
    green = 256

    def __init__(self, red = 255, blue = 255, green = 255, Brightness = 5):
        self.red = red
        self.blue = blue
        self.green = green
        self.Brightness = Brightness

    def __add__(self, other):
        r,b,g = self.red + other.red, self.blue + other.blue,self.green+ other.green
        if r > 255: r = 255
        if b > 255: b = 255
        if g > 255: g = 255
        return LightValue(r,b,g,self.Brightness + other.Brightness)
    def __div__(self,other):
        if isinstance(other,LightValue):
            return LightValue(self.red / other.red, self.blue / other.blue,self.green / other.green,self.Brightness / other.Brightness)
        else:
            return LightValue(int(math.ceil(self.red / other)), int(math.ceil(self.blue / other)), int(math.ceil(self.green / other)),int(math.ceil(self.Brightness / other)))

    def lightToLibtcodColor(self):
        r,b,g = self.red,self.blue,self.green
        if r > 255: r = 255
        if b > 255: b = 255
        if g > 255: g = 255
        return libtcod.Color(self.red,self.blue,self.green)


class LightSource:
    AREA_LIGHT = 1
    SPOT_LIGHT = 2

    value = LightValue()

    def __init__(self, red = 255, blue = 255, green = 255, Brightness = 5, lightType = AREA_LIGHT):
        self.value = LightValue(red,blue,green,Brightness)
        self.lightType = lightType



