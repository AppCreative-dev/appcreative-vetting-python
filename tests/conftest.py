import sys
from pathlib import Path

# Let the tests import the recommendations service.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "services" / "recommendations"))
