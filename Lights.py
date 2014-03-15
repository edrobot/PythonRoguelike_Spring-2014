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

class LightValue:
    Brightness = 0
    red = 256
    blue = 256
    green = 256

    def __init__(self, red = 256, blue = 256, green = 256, Brightness = 5):
        self.red = red
        self.blue = blue
        self.green = green
        self.Brightness = Brightness

    def __add__(self, other):
        return LightValue(self.red + other.red, self.blue + other.blue,self.green+ other.green,self.Brightness + other.Brightness)


class LightSource:
    AREA_LIGHT = 1
    SPOT_LIGHT = 2

    value = LightValue()

    def __init__(self, red = 256, blue = 256, green = 256, Brightness = 5, lightType = AREA_LIGHT):
        self.value = LightValue(red,blue,green,Brightness)
        self.lightType = lightType



