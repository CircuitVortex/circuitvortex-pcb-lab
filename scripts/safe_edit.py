#!/usr/bin/env python3
import argparse,json,shutil
from pathlib import Path
from common import save_json,utc_now
SUPPORTED={"remove_silkscreen","resize_via","move_component","move_footprint","change_track_width","delete_track","add_track","remove_dangling_track","repair_connection","refill_zones","remove_unused_via"}
ap=argparse.ArgumentParser(); ap.add_argument("operation"); ap.add_argument("pcb"); ap.add_argument("--output"); ap.add_argument("--parameters",default="{}")
a=ap.parse_args()
if a.operation not in SUPPORTED: raise SystemExit("Unsupported operation: "+a.operation)
src=Path(a.pcb); out=Path(a.output) if a.output else src.with_name(src.stem+"_modified"+src.suffix); shutil.copy2(src,out)
r={"status":"prepared","timestamp":utc_now(),"operation":a.operation,"input":str(src),"output":str(out),"parameters":json.loads(a.parameters),"note":"Output isolated; geometry-changing operations must be validated with KiCad DRC and DFM."}
save_json(out.with_suffix(out.suffix+".operation.json"),r); print(json.dumps(r,indent=2))
