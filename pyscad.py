import ctypes
openscad=ctypes.cdll.LoadLibrary('./libopenscad.so')

openscad.inst_module.restype = ctypes.c_void_p
openscad.export_stl.restype = ctypes.c_char_p
openscad.export_dxf.restype = ctypes.c_char_p
openscad.to_source.restype = ctypes.c_char_p

openscad.init()

class Value(ctypes.Union):
	_fields_ = [
		("dblValue", ctypes.c_double),
		("strValue", ctypes.c_char_p),
		("vecValue", ctypes.POINTER(ctypes.c_double)),
	]
	
class Arg(ctypes.Structure):
	_fields_ = [
		("name", ctypes.c_char_p),
		("type", ctypes.c_char),
		("vecLen", ctypes.c_int),
		("value", Value),
	]
	_anonymous_ = ("value",)
	
	def setFrom(self, val, name=None):
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
			print arr
			self.vecValue = arr
				
class SCADObject(object):
	def __init__(self, modname, *args, **kwargs):
		self.modname = modname
		if 'children' in kwargs:
			self.children = kwargs['children']
			del kwargs['children']
		else:
			self.children = []
		self.args = args
		self.kwargs = kwargs
		self.position = (0,0,0)
		
	def __add__(self, x):
		return union(self, x)

	def __sub__(self, x):
		return difference(self, x)

	def __mul__(self, x):
		return intersection(self, x)

	def _cpp_object(self):
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
		print self.modname, numargs, [(i.type, i.dblValue) for i in args], numchildren

		result = openscad.inst_module(self.modname, numargs, ctypes.byref(args), numchildren, ctypes.byref(children)) 
		if self.position != (0,0,0):
			modname = ctypes.c_char_p('translate')
			args = (Arg*1)()
			args[0].setFrom(self.position)
			children = (ctypes.c_void_p * 1)()
			children[0] = result
			result = openscad.inst_module('translate', 1, ctypes.byref(args), 1, children)
			
		print "created"
		return result
		
	def render(self):
		print "rendering"
		openscad.render(self._cpp_object())
		
	def export_stl(self, filename):
		err = openscad.export_stl(self._cpp_object(), filename)
		if err:
			raise ValueError(err)
			
	def export_dxf(self, filename):
		err = openscad.export_dxf(self._cpp_object(), filename)
		if err:
			raise ValueError(err)
			
	def to_source(self):
		return openscad.to_source(self._cpp_object())

class sphere(SCADObject):
	def __init__(self, radius, position = (0,0,0)):
		super(sphere, self).__init__(modname='sphere', r = radius)
		self.position = position

class cube(SCADObject):
	def __init__(self, size, position = (0,0,0)):
		super(cube, self).__init__(modname='cube', size = size)
		self.position = position

class cylinder(SCADObject):
	def __init__(self, height, radiusTop, radiusBottom = None, position = (0,0,0)):
		if radiusBottom == None:
			radiusBottom = radiusTop
		super(cylinder, self).__init__(modname='cylinder', h = height, r1 = radiusTop, r2 = radiusBottom)
		self.position = position

class union(SCADObject):
	def __init__(self, *children):
		super(union, self).__init__(modname='union', children=children)

class difference(SCADObject):
	def __init__(self, *children):
		super(difference, self).__init__(modname='difference', children=children)

class intersection(SCADObject):
	def __init__(self, *children):
		super(intersection, self).__init__(modname='intersection', children=children)
		
		


