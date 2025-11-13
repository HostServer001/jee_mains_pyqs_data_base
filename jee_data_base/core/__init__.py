from pathlib import Path
import importlib.util as lib

spec = lib.find_spec("jee_data_base")
loc = Path(spec.origin)
data_base_path = loc.parent
cache_path = data_base_path/"cache"

print(data_base_path)
print(cache_path)

from .data_base import DataBase
import .pdfy
from .chapter import Chapter
from .question import Question
from .filter import Filter
from .cache import Cache
from .utils import *

db_health = check_cache_health("DataBaseChapters")
embedidngs_health = check_cache_health("EmbeddingsChapters")

if db_health == False:
    download_cache("DataBaseChapters")
if embedidngs_health == False:
    download_cache("EmbeddingsChapters")