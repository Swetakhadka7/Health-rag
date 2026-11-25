import sys
import types
from pathlib import Path

# make `import api`, `import answer` etc. work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Stand-in for the search stack, so tests need no database, no models and no PDFs.
_fake_rerank = types.ModuleType("rerank")
_fake_rerank.rerank_search = lambda query, k=5, pool=20: []
sys.modules["rerank"] = _fake_rerank