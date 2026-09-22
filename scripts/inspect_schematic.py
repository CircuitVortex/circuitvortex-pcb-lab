import argparse
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('schematic'); a=ap.parse_args(); print({'file':a.schematic,'bytes':Path(a.schematic).stat().st_size})
