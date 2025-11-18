from pathlib import Path
import importlib.util as lib

spec = lib.find_spec("jee_data_base")
loc = Path(spec.origin)

data_base_path = loc.parent
cache_path = data_base_path/"cache"
schema_version = "v007"
EMBEDDINGS_LINK = "https://github.com/HostServer001/jee_mains_pyqs_data_base/releases/download/v007/1763101292-EmbeddingsChapters-v007.pkl"
DATABASE_LINK = "https://github.com/HostServer001/jee_mains_pyqs_data_base/releases/download/v007/1762787474-DataBaseChapters-v007.pkl"

from .data_base import DataBase
from .chapter import Chapter
from .question import Question
from .filter import Filter
from .cache import Cache
from .utils import *
from .types import *

db_health = check_cache_health("DataBaseChapters")
embedidngs_health = check_cache_health("EmbeddingsChapters")

if db_health == False:
    download_cache("DataBaseChapters")
if embedidngs_health == False:
    download_cache("EmbeddingsChapters")