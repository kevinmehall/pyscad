import pyscad

c = pyscad.cube(10)
s = pyscad.sphere(3, position=(10,10,10))
i = c+s

i.export_stl('./demo.stl')

print "Source:"
print i.to_source()
print ''

i.render()
