from pyscad import sphere, cylinder
from base import render_example
	
def example001(size=50, hole=25):
	cy_r = float(hole)/2
	cy_h = (float(size) * 2.5)/2
	
	s = sphere(size/2)
	c1 = cylinder(cy_h, cy_r, transforms={'rotate': (0, 0, 0)}, center=True)
	c2 = cylinder(cy_h, cy_r, transforms={'rotate': (90, 0, 0)}, center=True)
	c3 = cylinder(cy_h, cy_r, transforms={'rotate': (0, 90, 0)}, center=True)
	render_example(s-c1-c2-c3, 'example001')
	
if __name__ == "__main__":
	example001()