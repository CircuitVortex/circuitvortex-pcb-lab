from pathlib import Path
import re

def parse_pcb(path):
    text=Path(path).read_text(encoding="utf-8",errors="replace")
    if not text.lstrip().startswith("(kicad_pcb"): raise ValueError("Not a KiCad PCB")
    if text.count("(")!=text.count(")"): raise ValueError("Unbalanced KiCad syntax")
    return {
      "layers":sorted(set(re.findall(r'\(layer\s+"([^"]+)"',text))),
      "nets":[{"id":int(n),"name":name} for n,name in re.findall(r'\(net\s+(\d+)\s+"([^"]*)"\)',text)],
      "footprints":re.findall(r'\(footprint\s+"([^"]+)"',text),
      "references":re.findall(r'\(property\s+"Reference"\s+"([^"]*)"',text),
      "vias":len(re.findall(r'\(via\b',text)),
      "segments":len(re.findall(r'\(segment\b',text)),
      "pads":len(re.findall(r'\(pad\s+"',text)),
      "zones":len(re.findall(r'\(zone\b',text)),
      "file_size":len(text)
    }
