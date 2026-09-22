import unittest,tempfile
from pathlib import Path
from scripts.parse_kicad import parse_pcb
class T(unittest.TestCase):
 def test_parser(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.kicad_pcb'; p.write_text('(kicad_pcb (version 20240108) (generator pcbnew))')
   self.assertEqual(parse_pcb(p)['pads'],0)
if __name__=='__main__': unittest.main()
