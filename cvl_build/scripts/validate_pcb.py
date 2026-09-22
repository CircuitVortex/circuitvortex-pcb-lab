import argparse,json
from parse_kicad import parse_pcb
ap=argparse.ArgumentParser(); ap.add_argument("pcb"); a=ap.parse_args()
print(json.dumps({"status":"ok","board":parse_pcb(a.pcb)},indent=2))
