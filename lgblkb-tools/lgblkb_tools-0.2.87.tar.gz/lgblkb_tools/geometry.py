import os
from box import Box
import collections
import itertools
import json
import geojson
import geojsonio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyproj
import shapely.geometry as shg
import shapely.ops as shops
import shapely.wkb as shwkb
import shapely.wkt as shwkt
from functools import partial
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from . import log_support as logsup
from .global_support import Folder
# import visvalingamwyatt as vw

geom_kz_coarse=r'POLYGON ((59.501953125 51.39920565355378, 51.50390625 52.50953477032727, 46.40625 50.875311142200765, '\
               r'45.1318359375 48.516604348867475, 51.37207031249999 41.04621681452063, 56.4697265625 40.713955826286046, '\
               r'58.00781249999999 44.49650533109348, 68.466796875 40.04443758460856, 80.595703125 41.60722821271717, '\
               r'85.869140625 46.46813299215554, 89.1650390625 49.009050809382046, 77.2998046875 54.87660665410869, '\
               r'70.09277343749999 56.07203547180089, 60.1171875 54.316523240258256, 59.501953125 51.39920565355378))'
geom_kz=r'POLYGON ((69.5654296875 55.727110085045986, 60.64453125000001 54.213861000644926, '\
        r'60.941162109375 53.126998061776156, 59.64477539062499 51.93749209045435, 61.31469726562501 51.23440735163459, '\
        r'61.22680664062499 50.89610395554359, 60.00732421875 50.965346321637696, 59.58984374999999 50.736455137010665, '\
        r'58.348388671875 51.29627609493991, 56.304931640625 51.16556659836182, 55.73364257812499 50.72254683363231, '\
        r'54.64599609375 51.193115244645874, 52.33886718749999 51.84935276370605, 50.60302734375 51.86970795368951, '\
        r'48.394775390625 50.680797145321655, 48.69140625 50.05713877598689, 48.372802734375 49.930008124606886, '\
        r'47.63671875 50.56230444080573, 47.13134765625 50.324422739309384, 46.7578125 49.83798245308484, '\
        r'46.318359375 48.38544219115483, 47.21923828125 47.56911375866714, 47.98828124999999 47.628380027447136, '\
        r'48.603515625 46.965259400349275, 48.240966796875 46.63435070293566, 48.49365234375 42.293564192170095, '\
        r'52.49267578125 41.50034959128928, 54.11865234375 42.187829010590825, 55.48095703125 41.08763212467916, '\
        r'56.129150390625 41.244772343082076, 56.085205078125 44.933696389694674, 58.502197265625 45.48324350868221, '\
        r'59.80957031249999 44.933696389694674, 60.8642578125 44.32384807250689, 61.89697265624999 43.42100882994726, '\
        r'63.24829101562501 43.5326204268101, 64.92919921875 43.476840397778936, 65.775146484375 42.71473218539458, '\
        r'65.89599609375 41.86137915587359, 66.324462890625 41.763117447005875, 66.62109375 41.054501963290505, '\
        r'68.73046875 40.421860362045194, 68.807373046875 40.88029480552824, 71.180419921875 42.23665188032057, '\
        r'71.47705078125 42.62587560259137, 73.63037109375 42.309815415686664, 73.795166015625 42.94033923363181, '\
        r'75.684814453125 42.64204079304426, 77.6513671875 42.70665956351041, 78.892822265625 42.62587560259137, '\
        r'80.35400390625 42.00032514831621, 81.10107421874999 43.34914966389313, 80.43090820312499 44.91035917458495, '\
        r'82.880859375 45.1742925240767, 82.562255859375 45.598665689820635, 83.21044921875 46.965259400349275, '\
        r'85.14404296875 46.717268685073954, 85.95703125 47.15236927446393, 85.924072265625 48.20271028869972, '\
        r'86.748046875 48.545705491847464, 87.51708984375 49.33944093715546, 86.759033203125 50.035973672195496, '\
        r'85.58349609375 49.76707407366792, 83.56201171875 51.213765926935025, 81.947021484375 50.90303283111257, '\
        r'80.74951171875 51.50190410761811, 80.1123046875 51.01375465718821, 78.057861328125 53.38332836757156, '\
        r'76.86035156249999 53.97547425742953, 77.1240234375 54.51470449573694, 76.695556640625 54.55295156056188, '\
        r'73.992919921875 53.74221377343122, 73.883056640625 54.194583360162646, 72.158203125 54.508326500290735, '\
        r'71.466064453125 54.322931143263474, 71.378173828125 54.87028529268185, 70.916748046875 55.416543608580064, '\
        r'69.5654296875 55.727110085045986))'

# @with_logging()
def remove_redundants(polygons,redundancy_order=2.5,**kwargs):
	area_max=max([g.area for g in polygons])
	candidates=list()
	for g in list(polygons):
		if g.area==0 or np.log10(area_max/g.area)>redundancy_order:
			logsup.logger.debug('Redundant land is detected. Removing it...')
			continue
		g_ext=g.exterior
		# simple_logger.debug('g_ext:\n%s',g_ext)
		# xy=np.stack([np.array(arr) for arr in g_ext.xy]).T
		# xy=vw.simplify(xy,ratio=0.95)
		# g_ext=shg.LinearRing(xy)
		# simple_logger.debug('xy:\n%s',xy)
		# simple_logger.debug('xy:\n%s',xy)
		# x=np.array(x)
		# simple_logger.debug('x:\n%s',x)
		# simple_logger.debug('y:\n%s',y)
		# raise NotImplementedError
		# simple_logger.debug('xy:\n%s',xy)
		
		g_interiors=list()
		for g_interior in g.interiors:
			gint=shg.Polygon(g_interior)
			if gint.area==0 or np.log10(area_max/gint.area)>redundancy_order:
				logsup.logger.debug('Redundant hole is detected. Removing it...')
				continue
			g_interiors.append(g_interior)
		clean_g=shg.Polygon(g_ext,g_interiors)
		candidates.append(clean_g)
	
	return candidates

def get_crs(geojson_datum):
	crs_info=geojson_datum.crs.properties['name'].split(':')
	if not crs_info[-1].isnumeric():
		print(crs_info)
		raise NotImplementedError('Could not infer crs. crs_info = \n{}'.format(crs_info))
	return int(crs_info[-1])

def plot_polygon(polygon: shg.Polygon,label=None,ax=None,name='',**kwargs):
	if ax is None: plot=plt.plot
	else: plot=ax.plot
	default_opts=dict(lw=3)
	if label is None: labeler=lambda l:dict(default_opts,label=l)
	else: labeler=lambda l:dict(default_opts,label='{} {}'.format(label,l))
	plotter=lambda linestring,_label:plot(*linestring.xy,**dict(labeler(_label),**kwargs))
	plotter(polygon.exterior,'exterior')
	if name:
		x,y=polygon.exterior.xy
		target_point_index=list(x).index(min(x))
		
		plt.text(x[target_point_index],y[target_point_index],s=name)
	for i,p_i in enumerate(polygon.interiors):
		plotter(p_i,'interior {}'.format(i))

def plot_poly(p,**kwargs):
	if isinstance(p,shg.MultiPolygon):
		for p in p: plot_poly(p,**kwargs)
	plt.plot(*p.exterior.xy,**kwargs)

def convert_crs(coor_obj,_in: int,_out=4326):
	inproj,outproj=pyproj.Proj(init=f'epsg:{_in}'),pyproj.Proj(init=f'epsg:{_out}')
	converter=lambda xy:np.stack(pyproj.transform(inproj,outproj,*xy),axis=1).reshape(-1,2)
	polygons=list()
	if type(coor_obj) is np.ndarray:
		assert coor_obj.shape[1]==2,\
			"ndarray shape should be (-1,2), but shape={} is provided.".format(coor_obj.shape)
		return converter(np.split(coor_obj,2,axis=1))
	elif type(coor_obj) is shg.Polygon:
		coor_obj=shg.MultiPolygon([coor_obj])
		returner=lambda multipolygon:multipolygon[0]
	elif type(coor_obj) is shg.MultiPolygon:
		returner=lambda multipolygon:multipolygon
		pass
	else: raise NotImplementedError('No implementation for objects of type = {}'.format(type(coor_obj)))
	for g in coor_obj:
		interior_xys=[converter(interior.xy) for interior in g.interiors]
		polygons.append(shg.Polygon(converter(g.exterior.xy),interior_xys))
	return returner(shg.MultiPolygon(polygons))

def reproject_point(point,_in,_out):
	inproj,outproj=pyproj.Proj(init=f'epsg:{_in}'),pyproj.Proj(init=f'epsg:{_out}')
	return shg.Point(pyproj.transform(inproj,outproj,point.x,point.y))

def get_area(geom,in_epsg):
	geom_area=shops.transform(
		partial(
			pyproj.transform,
			pyproj.Proj(init=f'EPSG:{in_epsg}'),
			pyproj.Proj(proj='aea',lat1=geom.bounds[1],lat2=geom.bounds[3])),geom).area
	return geom_area

def clean_multipolygon(multipolygon: shg.MultiPolygon):
	geoms=list()
	tree=collections.defaultdict(list)
	# multipolygon=multipolygon.buffer(1e-3)
	for polygon in multipolygon:
		exterior_geom=shg.Polygon(polygon.exterior)
		geoms.append(exterior_geom)
		geoms.extend([shg.Polygon(x) for x in polygon.interiors])
	for g1,g2 in itertools.combinations(geoms,2):
		if g1.contains(g2):
			#
			# if tree.get(g1):
			# 	g1_obj=tree.get(g1)
			# 	if g1_obj.contains(g2):
			# 		tree[g1]=g1_obj.difference(g2)
			# 	pass
			# else:
			# 	tree[g1]=g1.difference(g2)
			tree[geoms.index(g1)].append(g2)
	
	clean_polygons=list()
	for shell_index,holes in tree.items():
		try:
			p=shg.Polygon(shg.LinearRing(geoms[shell_index].exterior.coords),
			              [shg.LinearRing(x.exterior.coords) for x in holes])
		except IndexError as exc:
			logsup.logger.debug('multipolygon:\n%s',multipolygon)
			logsup.logger.debug('geoms:\n%s',geoms)
			logsup.logger.debug('shell_index: %s',shell_index)
			raise exc
		geoms.pop(shell_index)
		
		for x in holes: geoms.remove(x)
		clean_polygons.append(p)
	
	# p=shg.Polygon(shg.LinearRing(geoms[shell_index].coords.xy),[shg.LinearRing(x.coords.xy) for x in holes])
	# clean_polygons.append(p)
	
	# result=g1.difference(g2)
	# simple_logger.info('result: %s',result)
	# simple_logger.debug('tree:\n%s',tree)
	
	return shg.MultiPolygon([*clean_polygons,*geoms])

class SpatialGeom:
	__protected_members=['name','data','geom_obj','box']
	
	@classmethod
	def from_geojson(cls,geojson_datum,crs_in=None,crs_out=4326,**kwargs):
		if isinstance(geojson_datum,str):
			geojson_datum=geojson.load(open(geojson_datum))
		if 'features' in geojson_datum.keys(): geometry=geojson_datum.features[0].geometry
		else: geometry=geojson_datum.geometry
		cad_land=SpatialGeom(shg.shape(geometry),**kwargs)
		if cad_land.geom_obj.is_empty:
			print('Empty entry detected.')
			return cad_land
		cad_land.data['epsg']=crs_out
		if not 'name' in kwargs: cad_land.name=geojson_datum['features'][0]['properties']['KAD_NOMER']
		if crs_in==crs_out: return cad_land
		elif crs_in is None:
			if 'crs' in geojson_datum.keys():
				crs_in=get_crs(geojson_datum)
				if crs_in==crs_out: return cad_land
			elif max(cad_land.geom_obj.bounds)>90:
				#print('Assuming input crs = epsg: 32643')
				#crs_in='epsg:32643'
				raise NotImplementedError(
					'No info to infer from. Please, specify incoming coordinate reference system.')
			else:
				#print('Assuming proper input crs, i.e. "epsg:4326".')
				#return cad_land
				raise NotImplementedError(
					'No info to infer from. Please, specify incoming coordinate reference system.')
		cad_land.convert_crs(crs_in,crs_out)
		return cad_land
	
	def convert_crs(self,_from: int,to=4326):
		if self.geom_obj.is_empty:
			print('Cannot convert empty shape.')
			return self
		if _from==to: return self
		multi_polygon=convert_crs(self.geom_obj,_from,to)
		#if inplace:
		self.geom_obj=multi_polygon
		return self
		# else:
		# 	return SpatialGeom(multi_polygon,redundancy_order=self.redundancy_order,
		# 	                   name=self.name)
		pass
	
	def __init__(self,geom_obj,name='',**kwargs):
		"""

		:param geom_obj: wkt/wkb string, ndarray or shapely Polygon/Multipolygon
		:param name: name
		:param kwargs:
		redundancy_order = 2.5
		"""
		if isinstance(geom_obj,str):
			try:
				geom_obj=shwkt.loads(geom_obj)
			except Exception as e:
				try:
					json_obj=geojson.loads(geom_obj)
					geom_obj=shg.shape(json_obj['features'][0]['geometry'])
				except Exception as e:
					from shapely import geos
					# geos.WKBWriter.defaults['include_srid']=True
					geom_obj=shwkb.loads(geom_obj,hex=True)
		
		if isinstance(geom_obj,shg.Polygon): geom_obj=shg.MultiPolygon([geom_obj])
		elif isinstance(geom_obj,np.ndarray):
			geom_obj=shg.MultiPolygon([shg.Polygon(geom_obj)])
		self.name=name# or 'SpatialGeom'
		self.data=Box(kwargs)
		if not geom_obj.is_empty: geom_obj=shg.MultiPolygon(remove_redundants(geom_obj,**kwargs))
		self.geom_obj: shg.MultiPolygon=clean_multipolygon(geom_obj)
		self.data['with_holes']=max(self.do_for_each(lambda p:len(list(p.interiors))),default=0)!=0
		pass
	
	def do_for_each(self,func,*args,**kwargs):
		doer=lambda x:func(x,*args,**kwargs)
		#if self.is_multipolygon:
		out=list()
		for p in self.geom_obj:
			out.append(doer(p))
		return out
	
	# else:
	# 	return [doer(self.geom_obj)]
	
	def show_on_geojsonio(self):
		get_displayed=lambda obj:geojsonio.display(json.dumps(shg.mapping(obj)))
		self.do_for_each(get_displayed)
	
	def plot(self,show=False,**kwargs):
		if self.geom_obj.is_empty: return
		# if ax is None: plot=plt.plot
		# else: plot=ax.plot
		# plotter=lambda linearring,label,:plot(*linearring.xy,**dict(dict(label=label),**kwargs))
		#if self.is_multipolygon:
		for i,p in enumerate(self.geom_obj):
			plot_polygon(p,**dict(dict(label='Polygon {}'.format(i),name=self.name),**kwargs))
		if show:
			plt.legend(loc='best')
			plt.show()
		return self
	
	def to_geojson(self,**kwargs):
		return geojson.Feature(geometry=self.geom_obj,**kwargs)
	
	def __bool__(self):
		return self.geom_obj.is_empty
	
	# else:
	# 	plot_polygon(self.geom_obj,'Single polygon',**kwargs)
	
	def get_area(self,in_epsg=4326):
		return get_area(self.geom_obj,in_epsg)
	
	def intersection(self,geom,name=None):
		if isinstance(geom,SpatialGeom): geom=geom.geom_obj
		return SpatialGeom(self.geom_obj.intersection(geom),name=name)
	
	def difference(self,geom,name=None):
		if isinstance(geom,SpatialGeom): geom=geom.geom_obj
		return SpatialGeom(self.geom_obj.difference(geom),name=name)
	
	def __getitem__(self,item):
		return self.data[item]
	
	def __iter__(self):
		return iter(self.data.keys())
	
	def __getattr__(self,item):
		if item in self.__protected_members: return self.__getattribute__(item)
		else: return self.data[item]
	
	@property
	def bounding_box(self):
		return SpatialGeom(shg.Polygon(self.geom_obj.envelope.exterior))
	
	def save(self,folder,filename=None,filepath=None):
		if filepath is None: filepath=Folder(folder).get_filepath(filename or self.name or 'SpatialGeom')
		if not os.path.splitext(filepath)[-1]: filepath=filepath+'.svg'
		plt.savefig(filepath,dpi=None,facecolor='w',edgecolor='w',
		            orientation='portrait',papertype=None,format=None,
		            transparent=False,bbox_inches=None,pad_inches=0.1,
		            frameon=None,metadata=None)
		plt.clf()
		return self
	
	def __str__(self):
		return '{}: {}'.format(self.name,str(self.geom_obj))
	
	def buffer(self,distance,resolution=16,quadsegs=None,cap_style=shg.CAP_STYLE.round,
	           join_style=shg.JOIN_STYLE.round,mitre_limit=5.0):
		return self.__class__(self.geom_obj.buffer(distance,resolution=resolution,quadsegs=quadsegs,
		                                           cap_style=cap_style,join_style=join_style,mitre_limit=mitre_limit))
#
# @property
# def holes(self):
# 	if self.__holes is None:
# 		self.__holes=[line_xy(x) for x in self.polygon.boundary[1:]]
# 	return self.__holes
#
# @property
# def all_xy(self):
# 	return np.concatenate([self.xy[:-1],*[x[:-1] for x in self.holes]])
#
# @property
# def xy(self):
# 	if self.__xy is None:
# 		if self.is_multilinestring:
# 			self.__xy=line_xy(self.polygon.boundary[0])
# 		else:
# 			self.__xy=line_xy(self.polygon.boundary)
# 	return self.__xy

def plot_patches(polygons,ax=None,c=None,**kwargs):
	if ax is None: ax=plt.gca()
	if isinstance(polygons,pd.Series):
		pcol=PatchCollection(polygons.map(lambda p:Polygon(p.exterior)),**kwargs)
	else:
		poly_objs=[Polygon(x.exterior) for x in polygons]
		pcol=PatchCollection(poly_objs,**kwargs)
	if c: pcol.set_color(c)
	ax.add_collection(pcol)

def get_rect(corner,sizes):
	corner=np.array(corner)
	sizes=np.array(sizes)
	return np.array([corner,corner+sizes*(1,0),corner+sizes,corner+sizes*(0,1)])

def get_portion(polygon,offset_ratio,size_ratio):
	p_min=np.array(polygon.bounds[0:2])
	p_max=np.array(polygon.bounds[-2:])
	curr_sizes=(p_max-p_min)
	new_rect=shg.Polygon(get_rect(p_min+curr_sizes*offset_ratio,curr_sizes*size_ratio))
	return new_rect

def get_forecast_region(cad_geom,min_forecast_point_dist=3,forecast_step_degrees=0.25):
	forecast_region=cad_geom.envelope.buffer(min_forecast_point_dist*forecast_step_degrees*1.2)
	return forecast_region.envelope

if __name__=='__main__':
	# p=shg.Point(78,43)
	# print(reproject_point(p,4326,3857))
	# print(p.x)
	pass

# a1=shg.Polygon(np.random.rand(4,2))
# a2=shg.Polygon()
# b1=shg.MultiPolygon()
# b2=shg.MultiPolygon([a1])
# b3=shg.MultiPolygon([a1,shg.Polygon(np.random.rand(4,2),[np.random.rand(3,2)])])
# c1=SpatialGeom(a1)
# #c2=c1.convert_crs(32642)
# print(convert_crs(np.random.rand(10,2),32642))
