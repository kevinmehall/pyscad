import ctypes
openscad=ctypes.cdll.LoadLibrary('./libopenscad.so')

openscad.inst_module.restype = ctypes.c_void_p


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
		elif isinstance(val, list):
			self.type = 'v'
			self.vecLen = ctypes.c_int(len(list))
			arr = (ctypes.double * len(list))()
			for i, v in enumerate(val):
				arr[i] = ctypes.c_double(v)
			self.vecValue = pointer(arr)
				
class SCADObject:
	def __init__(self, modname, *args, **kwargs):
		self.modname = modname
		if 'children' in kwargs:
			self.children = kwargs['children']
			del kwargs['children']
		else:
			self.children = []
			
		self.args = args
		self.kwargs = kwargs
		
	def cpp_object(self):
		modname = ctypes.c_char_p(self.modname)
		numargs = len(self.args) + len(self.kwargs)
		args = (Arg*numargs)()
		i = 0
		for a in self.args:
			args[i].setFrom(a)
			i += 1
		for n in self.kwargs:
			argarr[i].setFrom(kwargs[n], name=n)
			i += 1
		numchildren = len(self.children)
		children = (ctypes.c_void_p * numchildren)()
		for i, c in enumerate(self.children):
			children[i] = c.cpp_object()
		print numargs, [(i.type, i.dblValue) for i in args]
			
		return openscad.inst_module(modname, numargs, ctypes.pointer(args), numchildren, ctypes.pointer(children)) 
		
				
		

sphere = SCADObject('sphere', 10)
cube = SCADObject('cube', 10, 10, 10)
union = SCADObject('union', children=[sphere, cube])
openscad.render(union.cpp_object())

