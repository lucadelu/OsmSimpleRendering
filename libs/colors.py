#!/usr/bin/python
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

###########################################################################
###
# begin : 2011-01-02
# authors: Luca Delucchi
# copyright : (C) 2010 by luca delucchi
# email : lucadeluge@gmail.com
###

###
# This program is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License. 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License (GPL) for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
#  Free Software Foundation, Inc.,
#  59 Temple Place - Suite 330,
#  Boston, MA  02111-1307, USA.
###
############################################################################


from mapnik import Color
from conf import colorsAvaible, elementsRend

class outColors:
  """Class for calculate the output colors"""
  def __init__(self,
	      color):
    """ Initialization of class
    @ color is the color name to use
    """
    # variable for chosen color
    self.color = color
    # dictionary for avaible colors
    self.colors = colorsAvaible().colors 
    # dictionary for elements
    self.elements = elementsRend().elements

  def createColor(self):
    """ Function to return a dictionary with elements a its colors """
    # dictionary returned with element and associated color
    mapColor = {}
    # length of self.elements
    maxValue = len(self.elements)+1
    minValue = 1
    # for each element calculate the color and add it to mapColor
    for i in range(minValue,maxValue):
      red = self.colors[self.color]['max'][0] * ( i - minValue ) \
	/ ( maxValue - minValue ) + self.colors[self.color]['min'][0] \
	* ( maxValue - i ) / ( maxValue - minValue );
      green = self.colors[self.color]['max'][1] * ( i - minValue ) \
	/ ( maxValue - minValue ) + self.colors[self.color]['min'][1] \
	* ( maxValue - i ) / ( maxValue - minValue );
      blue =  self.colors[self.color]['max'][2] * ( i - minValue ) \
	/ ( maxValue - minValue ) + self.colors[self.color]['min'][2] \
	* ( maxValue - i ) / ( maxValue - minValue );
      mapColor[self.elements[i]] = Color(red,green,blue)
    return mapColor