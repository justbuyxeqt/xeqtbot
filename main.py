import sys

secrets_loaded = False
from secrets import *

if not secrets_loaded:
    print("Missing secrets.py. Aborting")
    sys.exit(1)

