import ctypes
_openscad=ctypes.cdll.LoadLibrary('./libopenscad.so')

_openscad.inst_module.restype = ctypes.c_void_p
_openscad.export_stl.restype = ctypes.c_char_p
_openscad.export_dxf.restype = ctypes.c_char_p
_openscad.to_source.restype = ctypes.c_char_p

_openscad.init()

class Value(ctypes.Union):
	"""A C++ OpenSCAD value."""
	_fields_ = [
		("dblValue", ctypes.c_double),
		("strValue", ctypes.c_char_p),
		("vecValue", ctypes.POINTER(ctypes.c_double)),
	]
	
class Arg(ctypes.Structure):
	"""A C++ OpenSCAD argument."""
	_fields_ = [
		("name", ctypes.c_char_p),
		("type", ctypes.c_char),
		("vecLen", ctypes.c_int),
		("value", Value),
	]
	_anonymous_ = ("value",)
	
	def setFrom(self, val, name=None):
		"""Create an argument using a value as input.
		
		Arguments:
		Value -- an OpenSCAD value
		string -- the name of the value
		"""
		if name:
			self.name = ctypes.c_char_p(name)
		else:
			self.name = ctypes.c_char_p(0)
			
		if isinstance(val, int) or isinstance(val, float):
			self.type = 'd'
			self.dblValue = ctypes.c_double(val)
		elif isinstance(val, str):
			self.type = 's'
			self.strValue = ctypes.c_char_p(val)
		elif isinstance(val, list) or isinstance(val, tuple):
			self.type = 'v'
			self.vecLen = ctypes.c_int(len(val))
			arr = (ctypes.c_double * len(val))()
			for i, v in enumerate(val):
				arr[i] = ctypes.c_double(v)
			self.vecValue = arr
				
class SCADObject(object):
	"""An OpenSCAD object."""
	def __init__(self, modname, *args, **kwargs):
		"""Create and display an OpenSCAD object. Not called directly,
		only by descendents.
		
		Arguments:
		string -- type of OpenSCAD object
		tuple -- tuple of arguments
		mixed -- any number of keyword arguments
		"""
		self.modname = modname
		if 'children' in kwargs:
			self.children = kwargs['children']
			del kwargs['children']
		else:
			self.children = []
		self.args = args
		self.kwargs = kwargs
		self.position = (0,0,0)

	#overload addition, subtraction, multiplication for SCADObjects		
	def __add__(self, x):
		"""OpenSCAD addition.
		
		Arguments:
		SCADObject -- the object to add to the current object
		"""
		return union(self, x)

	def __sub__(self, x):
		"""OpenSCAD subtraction.
		
		Arguments:
		SCADObject -- the object to subtract from the current object
		"""
		return difference(self, x)

	def __mul__(self, x):
		"""OpenSCAD multiplication.
		
		Arguments:
		SCADObject -- the object to multiply by the current object
		"""
		return intersection(self, x)

	def _cpp_object(self):
		"""The C++ representation of this object."""
		numargs = len(self.args) + len(self.kwargs)
		args = (Arg*numargs)()
		i = 0
		for a in self.args:
			args[i].setFrom(a)
			i += 1
		for n in self.kwargs:
			args[i].setFrom(self.kwargs[n], name=n)
			i += 1
		numchildren = len(self.children)
		children = (ctypes.c_void_p * numchildren)()
		for i, c in enumerate(self.children):
			children[i] = c._cpp_object()

		result = _openscad.inst_module(self.modname, numargs, ctypes.byref(args), numchildren, ctypes.byref(children)) 
		if self.position != (0,0,0):
			modname = ctypes.c_char_p('translate')
			args = (Arg*1)()
			args[0].setFrom(self.position)
			children = (ctypes.c_void_p * 1)()
			children[0] = result
			result = _openscad.inst_module('translate', 1, ctypes.byref(args), 1, children)
			
		return result
		
	def render(self):
		"""Render and display what you have made."""
		_openscad.render(self._cpp_object())
		
	def export_stl(self, filename):
		"""Export what you have made to an .stl file, only works if
		what you have made is 3D.
		"""
		err = _openscad.export_stl(self._cpp_object(), filename)
		if err:
			raise ValueError(err)
			
	def export_dxf(self, filename):
		"""Export what you have made to a .dxf file, only works if
		what you have made is 2D.
		"""
		err = _openscad.export_dxf(self._cpp_object(), filename)
		if err:
			raise ValueError(err)
			
	def to_source(self):
		"""return what you have made as a scad string"""
		return _openscad.to_source(self._cpp_object())

class sphere(SCADObject):
	"""An OpenSCAD sphere."""
	def __init__(self, radius, position = (0,0,0)):
		"""Create and display a sphere.
		
		Arguments:
		real -- the radius
		tuple -- the position
		"""		
		super(sphere, self).__init__(modname='sphere', r = radius)
		self.position = position

class cube(SCADObject):
	"""An OpenSCAD cube."""
	def __init__(self, size, position = (0,0,0)):
		"""Create and display a cube.
		
		Arguments:
		real or tuple -- the size
		tuple -- the position
		"""
		super(cube, self).__init__(modname='cube', size = size)
		self.position = position

class cylinder(SCADObject):
	"""An OpenSCAD cylinder."""	
	def __init__(self, height, radiusTop, radiusBottom = None, position = (0,0,0)):
		"""Create and display a cylinder.
		
		Arguments:
		real -- the height
		real -- the radius of the top of the cylinder
		real -- the radius of the bottom of the cylinder
		tuple -- the position
		"""
		if radiusBottom == None:
			radiusBottom = radiusTop
		super(cylinder, self).__init__(modname='cylinder', h = height, r1 = radiusTop, r2 = radiusBottom)
		self.position = position

class union(SCADObject):
	"""An OpenSCAD union."""
	def __init__(self, *children):
		"""Create and display a union of objects
		
		Arguments:
		tuple -- objects to union
		"""
		super(union, self).__init__(modname='union', children=children)

class difference(SCADObject):
	"""An OpenSCAD difference."""
	def __init__(self, *children):
		"""Create and display a difference of objects
		
		Arguments:
		tuple -- objects to difference
		"""
		super(difference, self).__init__(modname='difference', children=children)

class intersection(SCADObject):
	"""An OpenSCAD intersection."""
	def __init__(self, *children):
		"""Create and display an intersection of objects
		
		Arguments:
		tuple -- objects to intersect
		"""
		super(intersection, self).__init__(modname='intersection', children=children)
		
		


