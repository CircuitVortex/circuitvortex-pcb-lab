#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from parse_kicad import parse_pcb
try:
    from scripts.common import save_json,result
except ImportError:
    from common import save_json,result
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("pcb"); ap.add_argument("-o","--output")
    a=ap.parse_args()
    r=result("ok",input=a.pcb,board=parse_pcb(a.pcb),warnings=[])
    if a.output: save_json(a.output,r)
    print(json.dumps(r,indent=2))
if __name__=="__main__": main()
