import argparse,shutil
ap=argparse.ArgumentParser(); ap.add_argument("input"); ap.add_argument("output"); a=ap.parse_args(); shutil.copy2(a.input,a.output); print("Prepared:",a.output)
