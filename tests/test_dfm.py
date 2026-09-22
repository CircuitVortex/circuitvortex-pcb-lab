import unittest,tempfile
from pathlib import Path
from scripts.dfm_check import check
class T(unittest.TestCase):
 def test_dfm(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.kicad_pcb'; p.write_text('(kicad_pcb (version 20240108))')
   self.assertGreaterEqual(check(p)['issue_count'],1)
if __name__=='__main__': unittest.main()
