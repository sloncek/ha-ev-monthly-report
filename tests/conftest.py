"""Exercise the engine without importing the Home Assistant runtime package."""
import sys
from pathlib import Path
from types import ModuleType

_ROOT = Path(__file__).parents[1] / "custom_components"
for name, path in (("custom_components", _ROOT), ("custom_components.energy_ledger", _ROOT / "energy_ledger")):
    module = ModuleType(name)
    module.__path__ = [str(path)]
    sys.modules[name] = module
