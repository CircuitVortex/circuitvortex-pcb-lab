from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).parents[1]
def test_remove_silkscreen_changes_geometry(tmp_path):
    src=tmp_path/'a.kicad_pcb'; src.write_text('(kicad_pcb (version 20240108) (generator pcbnew)\n (gr_text "HELLO" (at 1 1) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))\n)')
    out=tmp_path/'b.kicad_pcb'; r=subprocess.run([sys.executable,str(ROOT/'scripts/safe_edit.py'),'remove_silkscreen',str(src),'--output',str(out)],capture_output=True,text=True)
    assert r.returncode==0 and 'F.SilkS' not in out.read_text()
