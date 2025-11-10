from core import Cache
from core.data_base import cache_path,schema_version

cache = Cache(cache_path,schema_version)

lol = cache.load_cache_pkl("EmbeddingsChapters")