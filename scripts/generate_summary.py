import argparse,json
from pathlib import Path
from common import save_json,utc_now
ap=argparse.ArgumentParser(); ap.add_argument("--inspect"); ap.add_argument("--dfm"); ap.add_argument("-o","--output",default="reports/summary.json"); a=ap.parse_args()
r={"timestamp":utc_now(),"stages":{}}
for n,p in (("inspection",a.inspect),("dfm",a.dfm)):
    if p and Path(p).exists(): r["stages"][n]=json.loads(Path(p).read_text())
save_json(a.output,r); print(json.dumps(r,indent=2))
