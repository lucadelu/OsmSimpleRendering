#!/usr/bin/python
# -*- coding: utf-8 -*-

###########################################################################
###
# begin : 2011-01-02
# authors: Luca Delucchi
# copyright : (C) 2010 by luca delucchi
# email : lucadeluge at gmail dot com
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
###########################################################################

from mapnik import *
from colors import *
from conf import *
import os, subprocess

class mapOut:
  """ Initial class for rendering """
  def __init__(self,
	      heightM,
	      widthM,
	      x,
	      y,
	      epsgCode,
	      color,
	      ppi = 300):

    # resoluzione in pixel
    self.m2pix = self.resPixel(ppi)
    # width in pixel
    self.widthPix = self.mToPixel(widthM,ppi)
    # heigth in pixel    
    self.heightPix = self.mToPixel(heightM,ppi)
    # mapnik map
    self.mapnikMap = Map(self.widthPix, self.heightPix)
    # UTM projection to calculate correctly distances
    self.projUTM = Projection('+init=epsg:' + str(epsgCode))
    # coord element for the center
    self.pointCoord = Coord(x,y)
    # color name used
    self.color = color 
    # elements contained in conf file
    self.elems = elementsRend()    
    # color map for elements
    try:
      self.mapColors = outColors(self.color).createColor()
    except EOFError:
      print "The color used is not in colorsAvaible in the conf file"
    # set background
    self.mapnikMap.background = self.mapColors['Back']
    # widths for element rendering
    self.rendDim = dimension().widths
    # set image path to None
    self.imagePath = None
    
  def bboxOut(self,mapScale = 5000):
    """ Set the bounding box for the rendering map using the scale and the 
    resolution depending from ppi
    @ mapScale : the map scale to use for calculate the bounding box
    """
    # calculate the width in meters
    distWidth = self.widthPix * self.m2pix * mapScale
    # calculate the heigth in meters  
    distHeigth = self.heightPix *  self.m2pix * mapScale
    # trasform the latlong point to utm
    poiUTM = self.pointCoord.forward(self.projUTM)
    # set the low left point
    ll = Coord(poiUTM.x - (distWidth / 2), poiUTM.y - (distHeigth / 2))
    # set the top rigth point
    tr = Coord(poiUTM.x + (distWidth / 2), poiUTM.y + (distHeigth / 2))
    # create a bounding box with envelope
    self.bbox_LL = Envelope(ll.inverse(self.projUTM),tr.inverse(self.projUTM))
    # set the bounding box to the map
    self.mapnikMap.zoom_to_box(self.bbox_LL)
    
  def resPixel(self,ppi):
    """
    @ ppi : the ppi value
    """
    return 0.0254 / ppi
     
  def mToPixel(self,m, ppi):
    """ Return the pixel 
    @ m : value of distance in meters
    @ ppi : the ppi value
    """
    return int(m / self.resPixel(ppi))

  def ruleStyleLayer(self,symb,filt,name, datasource):
    """ Add symbology to the layer and this to the mapnik map 
    @ symb : a mapnik symbology
    @ filt : a mapnik filter
    @ name : name of the element rendered
    @ datasource : a mapnik datasource    
    """
    # create rule
    ru = Rule()
    # if there is a filter, add it to rule
    if filt:
      ru.filter = filt
    # append the symbology to rule
    ru.symbols.append(symb)    
    # create style
    st = Style()
    # append rule to style
    st.rules.append(ru)
    # create layer
    la = Layer(name)
    # add datasource to layer
    la.datasource = datasource
    # append style to mapnik map
    self.mapnikMap.append_style(name,st)
    # append style to layer
    la.styles.append(name)
    # append layer to mapnik map
    self.mapnikMap.layers.append(la)

  def svgToPng(self,name,width,imagepath,removeBack=False,color=None):
    """ Convert svg icons to png 
    @ name : name of the element rendered
    @ width : dimension for the icon
    @ imagepath : the path to image
    @ removeBack : this variable it used by pointCoord function to remove 
		   the background
    @ color : variable to pass a color to using instead the one definited in 
	      colors
    """
    # if the color is not passed, it use the color defined by colors.createColor
    if not color:
      color = self.mapColors['Point'].to_hex_string()
    # input filename
    inFilename = imagepath + name + ".svg"
    # output filename
    outFilename = imagepath + name + ".png"
    if self.color == 'red2yellow' or self.color == 'green2blue':
      # create a list with the parameter to create white and black icons
      args = ['convert', inFilename, '-negate', '-scale', str(width)]
    else:
      # create a list with the parameter to create white and black icons
      args = ['convert', inFilename, '-fuzz', '40', '-fill', color, '-opaque', \
      '#111111', '-scale' , str(width)]
    # this is used for icon created by poiCoord function to remove the background
    if removeBack:
      # add -transparent option
      args.append('-transparent')
      # in this case the background is black
      if self.color == 'red2yellow' or self.color == 'green2blue':
	args.append('black')
      # in this case the background is white
      else:
	args.append('white')
    # append the output filename
    args.append(outFilename)
    # launch convert command
    result = subprocess.call(args)

  def lineFill(self,element, datasource):
    """ Add fill line rendering 
    @ element : a dictionary with name of element for self.mapColors and a 
	      string for the filter
    @ datasource : datasource created by conf
    """   
    # create the stroke for line
    fill = Stroke()
    # set color and width for symbology
    fill.color = self.mapColors[element.keys()[0]]
    fill.width = self.rendDim[element.keys()[0]]
    # set the line cap and line join
    fill.line_cap = line_cap.ROUND_CAP
    fill.line_join = line_join.ROUND_JOIN
    # if element is Rail set the dashes IT DOESN'T WORK
    if element.keys()[0] == 'Rail':
      fill.add_dash(10,10)
      fill.width = fill.width - 4
      fill.line_cap = line_cap.BUTT_CAP
    # if element is Steps set the dashes IT DOESN'T WORK    
    if element.keys()[0] == 'Steps':
      fill.add_dash(5,2)   
      fill.line_cap = line_cap.BUTT_CAP      
    # create symbology with stroke  
    sym = LineSymbolizer(fill)
    # create filter
    fil = Filter(element[element.keys()[0]])
    # add element to the mapnik map
    self.ruleStyleLayer(sym,fil,element.keys()[0] + '_fill', datasource)

  def lineBord(self,element, datasource):
    """ Add border line rendering 
    @ element : a dictionary with name of element for self.mapColors and a 
	      string for the filter
    @ datasource : datasource created by conf    	      
    """
    # create the stroke for line   
    border = Stroke()
    # set color and width for symbology    
    border.color = self.mapColors['Border']
    border.width = self.rendDim[element.keys()[0]] + 2
    # set the line cap and line join    
    border.line_cap = line_cap.ROUND_CAP
    border.line_join = line_join.ROUND_JOIN
    # if element is Path set the dashes IT DOESN'T WORK        
    if element.keys()[0] == 'Path':
      border.add_dash(.1,.1)
    # create symbology with stroke     
    sym = LineSymbolizer(border)
    # create filter
    fil = Filter(element[element.keys()[0]])
    # add element to the mapnik map
    self.ruleStyleLayer(sym,fil,element.keys()[0] + '_border', datasource)
       
  def polygon(self, element, datasource):
    """ Add border line rendering 
    @ element : a dictionary with name of element for self.mapColors and a 
	      string for the filter
    @ datasource : datasource created by conf    
    """
    # create polygon symbology
    sym = PolygonSymbolizer(self.mapColors[element.keys()[0]])
    # create filter
    fil = Filter(element[element.keys()[0]])
    # add element to the mapnik map
    self.ruleStyleLayer(sym,fil,element.keys()[0] + '_polygon', datasource)
    
  def point(self, element, datasource, imagepath = './symbol/', color=None):
    """ Add point elements
    @ element : a dictionary with name of element for self.mapColors and a 
	      string for the filter
    @ datasource : datasource created by conf 
    @ imagepath : the path to image
    @ color : variable to pass a color to using instead the one definited in 
	      colors    
    """
    # set the width for point
    width = self.rendDim['Point']
    # set the name
    nameEle = element.keys()[0]
    # set the path to image
    self.imagePath = imagepath
    # convert svg to png
    self.svgToPng(nameEle,width,self.imagePath,color=color)
    # create point symbology
    sym = PointSymbolizer(self.imagePath + nameEle + '.png', 'png', width,width)
    #sy.allow_overlap = True
    # create filter
    fil = Filter(element[nameEle])
    # add element to the mapnik map
    self.ruleStyleLayer(sym,fil, nameEle + '_poi', datasource)      

  def poiList(self, elements, datasource, imagepath = './symbol/', color=None):
    """ Add point element for a list 
    @ elements : a list of dictionary with name of element for self.mapColors 
		and a string for the filter
    @ datasource : datasource created by conf 
    @ imagepath : the path to image
    @ color : variable to pass a color to using instead the one definited in 
	      colors    
    """
    for i in elements:
      self.point(i,datasource,imagepath,color)     

  def poiCoord(self,element, imagepath = './symbol/',color=None):
    """ Add point element with the icon for 'I am here' or 'I was here' 
    @ elements : a text to chose between iamhere, iwashere
    @ imagepath : the path to image
    @ color : variable to pass a color to using instead the one definited in 
	      colors    
    """
    # set the path to image    
    self.imagePath = imagepath
    # create a point datasource
    pd = PointDatasource()
    # add point
    pd.add_point(self.pointCoord.x,self.pointCoord.y,'TYPE','symbol')
    # convert svg icon to png
    self.svgToPng(element,self.rendDim['Icon'],self.imagePath,True,color)
    # create point symbology
    sym = PointSymbolizer(self.imagePath + element + '.png', 'png', \
    self.rendDim['Icon'], self.rendDim['Icon'])
    # add point to the mapnik map
    self.ruleStyleLayer(sym, None, element + '_poiCoor', pd)

  def text(self, element, datasource, label_place = label_placement.LINE_PLACEMENT):
    """ Add text element
    @ element : a dictionary with name of element for self.mapColors and a 
	      string for the filter
    @ datasource : datasource created by conf 
    @ label_place : a mapnik label_placement object 
    """
    # set width
    width = self.rendDim[element.keys()[0]] + 1
    # create text symbology
    tx = TextSymbolizer('name', 'DejaVu Sans Book', width, Color('white'))
    # set the placement
    tx.label_placement = label_place
    # create filter
    fil = Filter(element[element.keys()[0]])
    # add element to the mapnik map
    self.ruleStyleLayer(tx, fil, element.keys()[0] + '_text', datasource)

  def rendering(self, outputPath, imageType = 'png'):
    """ Create the output map
    @ outputPath : the output path
    @ imageType : the type of image output
    """
    render_to_file(self.mapnikMap,outputPath,imageType)
      


    
    