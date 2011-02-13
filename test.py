import pyscad

c = pyscad.cube(10)
s = pyscad.sphere(3, position=(10,10,10))
i = c+s

i.export_stl('/tmp/test.dxf')

print "Source:"
print i.to_source()
print ''

i.render()