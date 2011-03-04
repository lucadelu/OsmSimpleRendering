#!/usr/bin/python
# -*- coding: utf-8 -*-

###########################################################################
###
# begin : 2011-01-02
# authors: Luca Delucchi
# copyright : (C) 2011 by luca delucchi
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
############################################################################


# this is the file for configuration, you must change the values 

from mapnik import *

class confPostgis:
  """ Class to create the connections to postgis database 
  IMPORTANT: you must change the values for your connections
  """
  def __init__(self,extent):
    """ Initialitation of class
    @ extent a mapnik Envelope element
    @ you must set some variables
    """
    self.host = 'localhost'
    self.dbname = 'DBNAME'
    self.user = 'USERNAME'
    self.password = 'PASSWORD'
    self.prefixTable = 'PREFIX'
    self.geomColumn = 'way'
    self.srid = '4326'
    self.extentStr = str((extent.minx-1)) + ',' + str((extent.miny-1)) + ',' \
      + str((extent.maxx+1)) + ',' +str((extent.maxy+1))
   
  def lineConn(self):
    """ Define the connection for line table """
    # this is the query to order the line in order by length of geometry
    query = '%s_line where way && !bbox! ORDER BY st_LENGTH(%s) ASC' \
      % (self.prefixTable, self.geomColumn)
    datasource_line = PostGIS(host = self.host,
				dbname = self.dbname,
				user = self.user,
				password = self.password,
				table = query,
				srid = self.srid,
				geometry_field = self.geomColumn,
				extent = self.extentStr)
    return datasource_line
   
  def pointConn(self):  
    """ Define the connection for point table """
    datasource_point = PostGIS(host = self.host,
				dbname = self.dbname,
				user = self.user,
				password = self.password,
				table=self.prefixTable + '_point')
    return datasource_point
    
  def polygonConn(self):
    """ Define the connection for polygon table """
    datasource_polygon = PostGIS(host = self.host,
				dbname = self.dbname,
				user = self.user,
				password = self.password,
				table=self.prefixTable + '_polygon')
    return datasource_polygon    
    
class worlBound:
  """ Class to create the connection for the world boundaries 
  IMPORTANT: you must change the value for your connections
  """
  def __init__(self):
    """ Initialitation of class 
    @ you must set the path to vector world boundaries
    """
    self.path = 'path_to_world_boundaries'
    
  def worldConn(self):
    """ Function to return the ogr datasource """
    datasource_world = Ogr(file=self.path)
    return datasource_world
    
class elementsRend:
  """ Class for create classes of colors, each value will have a filter 
      to query the data
  """
  def __init__(self):
    """ Set elements variable """
    self.elements = {1 : 'Back', 2 : 'World', 3 : 'Water', 4 : 'Green', \
    5 : 'Path', 6 : 'Steps', 7 : 'PriWay', 8 : 'SecWay', 9 : 'Ferry', 10 : \
    'Build', 11 : 'Border', 12 : 'Point'}
    
  def build(self):
    """ return build query """
    return {'Build': "[building] = 'yes'"}
    
  def green(self):
    """ return green polygon query """
    return {'Green': "[landuse] = 'green' or [landuse] = 'forest' or " \
    "[landuse] = 'village_green' or [natural] = 'wood' or [natural] = 'park'" \
    " or [natural] = 'forest' or [leisure] = 'park' or [leisure] = 'garden' " \
    "or [leisure] = 'stadium'"}
    
  def water(self):
    """ return water query """
    return {'Water':"(([waterway] = 'stream' or [waterway] = 'river' or " \
    "[waterway] = 'riverbank' or [waterway] = 'canal') and [tunnel] != 'yes')" \
    "or [natural] = 'water'"}
    
  def path(self):
    """ return path query """
    return {'Path': "([highway] = 'track' or [highway] = 'footway' or " \
    "[highway] = 'cycleway' or [highway] = 'path' or [highway] = 'pedestrian')" \
    " and not ([tunnel] = 'yes' or [tunnel] = 'true')"}

  def path_tunnel(self):
    """ return path query """
    return {'Path_tunnel': "([highway] = 'track' or [highway] = 'footway' or " \
    "[highway] = 'cycleway' or [highway] = 'path' or [highway] = 'pedestrian')" \
    " and [tunnel] = 'yes'"}

  def steps(self):
    """ return path query """
    return {'Steps': "[highway] = 'steps'"} 
    
  def rail(self):
    """ return rail query """
    return {'Ferry' : "([railway] = 'rail' or [railway] = 'tram' or [railway] " \
    "= 'ligth_tram' or [railway] = 'subway' or [railway] = 'funicular') and " \
    "not ([tunnel] = 'yes' or [tunnel] = 'true')"}
    
  def rail_tunnel(self):
    """ return rail query """
    return {'Ferry_tunnel' : "([railway] = 'rail' or [railway] = 'tram' or " \
    "[railway] = 'ligth_tram' or [railway] = 'subway' or [railway] = " \
    "'funicular') and [tunnel] = 'yes'"}    
    
  def pri_way(self):
    """ return street query """
    return {'PriWay':"([highway] = 'motorway' or [highway] = 'motorway_link'" \
    "or [highway] = 'trunk' or [highway] = 'trunk_link' or [highway] = " \
    "'primary' or [highway] = 'primary_link') and not ([tunnel] = 'yes' or " \
    "[tunnel] = 'true')"}
    
  def sec_way(self):
    """ return street query """
    return {'SecWay':"([highway] = 'secondary' or " \
    "[highway] = 'tertiary' or [highway] = 'unclassified' or " \
    "[highway] = 'residential' or [highway] = 'road') and not ([tunnel] = " \
    "'yes' or [tunnel] = 'true')"}

  def pri_way_tunnel(self):
    """ return street query """
    return {'PriWay_tunnel':"([highway] = 'motorway' or [highway] = " \
    "'motorway_link' or [highway] = 'trunk' or [highway] = 'trunk_link' or " \
    "[highway] = 'primary' or [highway] = 'primary_link') and ([tunnel] = " \
    "'yes' or [tunnel] = 'true')"}
    
  def sec_way_tunnel(self):
    """ return street query """
    return {'SecWay_tunnel':"([highway] = 'secondary' or " \
    "[highway] = 'tertiary' or [highway] = 'unclassified' or " \
    "[highway] = 'residential' or [highway] = 'road') and ([tunnel] = 'yes' " \
    "or [tunnel] = 'true')"}

  def pri_way_bridge(self):
    """ return street query """
    return {'PriWay_tunnel':"([highway] = 'motorway' or [highway] = " \
    "'motorway_link' or [highway] = 'trunk' or [highway] = 'trunk_link' or " \
    "[highway] = 'primary' or [highway] = 'primary_link') and ([bridge] = " \
    "'yes' or [bridge] = 'true')"}

  def sec_way_bridge(self):
    """ return street query """
    return {'SecWay_tunnel':"([highway] = 'secondary' or " \
    "[highway] = 'tertiary' or [highway] = 'unclassified' or " \
    "[highway] = 'residential' or [highway] = 'road') and ([bridge] = 'yes' " \
    "or [bridge] = 'true')"}

  def pri_way_layer(self,num):
    """ return street query 
    @ num : number of layer
    """
    return {'PriWay_tunnel':"([highway] = 'motorway' or [highway] = " \
    "'motorway_link' or [highway] = 'trunk' or [highway] = 'trunk_link' or " \
    "[highway] = 'primary' or [highway] = 'primary_link') and ([bridge] = " \
    "'yes' or [bridge] = 'true'"}

  def poiSleep(self):
    """ return sleep point queries """
    return [{'accommodation_hotel' : "[tourism] = 'hotel' or [tourism] = "\
    "'motel'"},{'accommodation_camping' : "[tourism] = 'camp_site'"}, \
    {'accommodation_youth_hostel' : "[tourism] = 'hostel'"}, \
    {'accommodation_caravan_park' : "[tourism] = 'caravan_site'"}]
    
  def poiTrasport(self):
    """ return transportation point queries """    
    return [{'transport_train_station':"[railway] = 'station' or [railway] =" \
    "'halt'"},{'transport_train_station2' : "[railway] = 'subway_entrance'"}, \
    {'transport_bus_station' : "[amenity] = 'bus_station' or [highway] = " \
    "'bus_stop'"},{'transport_airport':"[aeroway] = 'aerodrome'"}]

  def poiService(self):
    """ return services point queries """    
    return  [{'amenity_recycling' : "[amenity]='recycling'"}, {'money_bank' : \
    "[amenity]='bank'"}, {'amenity_post_office' : "[amenity]='post_office'"}, \
    {'health_hospital_emergency':"[amenity]='hospital'"}]

  def poiEatDrink(self):
    """ return eat/drink point queries """    
    return [{'food_pub' : "[amenity] = 'pub'"}, {'food_restaurant' : \
    "[amenity] = 'restaurant'"}, {'food_drinkingtap' :"[amenity]='drinking_water'"}]
  
  def poiTourism(self):
    """ return tourism point queries, it add by default sleep, transport ù
    and eat/drink points """
    turism = [{'tourist_view_point': "[tourism] = 'viewpoint'"}, \
    {'tourist_picnic': "[tourism] = 'picnic_site'"}, {'tourist_museum': \
    "[tourism] = 'museum'"}, {'tourist_castle': "[historic] = 'castle'"}, \
    {'tourist_monument': "[historic] = 'monument'"}]
    turism.extend(self.poiSleep())
    turism.extend(self.poiTrasport())
    turism.extend(self.poiEatDrink())
    return turism
    
  def poiCar(self):
    """ return car point queries """    
    return [{'transport_parking' : "[amenity] = 'parking'"}, \
    {'transport_fuel' : "[amenity] = 'fuel'"}, {'transport_car_share' : \
    "[amenity] = 'car_sharing'"}, {'transport_rental_share' : "[amenity] = " \
    "'car_rental'"}]
    
  def poiBicy(self):
    """ return bicycle point queries """    
    return [{'transport_parking_bicycle' : "[amenity] = 'bicycle_parking'"}, \
    {'transport_rental_bicycle' : "[amenity] = 'bicycle_rental'"}]
    
  def addr(self):
    """ return address point queries """    
    return [{'address' : "[amenity] = 'bicycle_parking'"}, \
    {'transport_rental_bicycle' : "[amenity] = 'bicycle_rental'"}]    
    
class colorsAvaible:
  """ Class to set colors avaible to rendering, you can add your 
      min and max value and after with outColor class create a graduated
      classification of colors
  """
  def __init__(self):
    blue = {'min' : [0,255,255], 'max' : [0,0,255]}
    gray = {'min' : [180,180,180], 'max' : [80,80,80]}
    green = {'min': [0,255,0], 'max' : [0,70,0]}
    red =  {'min' : [255,0,0], 'max' : [110,0,0]}
    wb = {'min' : [255,255,255], 'max' : [0,0,0]}
    red2yellow = {'min' : [255,0,0], 'max' : [255,255,0]}
    green2blue = {'min': [0,255,0], 'max' : [0,0,255]}
    blue2green = {'min': [0,0,255], 'max' : [0,255,0]}
    self.colors = {'blue' : blue, 'gray' : gray, 'green' : green, 'red' : red, \
		  'wb' : wb, 'red2yellow' : red2yellow, 'green2blue' : \
		  green2blue, 'blue2green' : blue2green}
    
class dimension:
  """ Class to set the dimension of elements
  """
  def __init__(self):
    self.widths = {'Water' : 8, 'PriWay' : 11, 'SecWay' : 9, 'Path' : 7, 
    'Steps' : 7, 'Ferry' : 9, 'Point' : 15, 'PointText' : 7, 'Icon' : 80}
