import unittest
from scripts.pcb_geometry import annular_ring,distance
class T(unittest.TestCase):
 def test_ring(self): self.assertAlmostEqual(annular_ring(.8,.4),.2)
 def test_dist(self): self.assertAlmostEqual(distance((0,0),(3,4)),5)
if __name__=='__main__': unittest.main()
