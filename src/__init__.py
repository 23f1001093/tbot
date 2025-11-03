import sys
import os

# Add compatibility modules for Python 3.13
compat_path = os.path.join(os.path.dirname(__file__), 'compat')
if compat_path not in sys.path:
    sys.path.insert(0, compat_path)
