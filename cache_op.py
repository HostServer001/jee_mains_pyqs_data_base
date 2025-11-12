"""
Do not run this file unless you know what you are doing
This file genrates embeddings for the questions and create cache files
Running this file is a computationally heavy task and waste of time.
The precompute embeddings are provided in cache folder
"""

import time
from core import DataBase, Cache, Filter
import core.data_base as db_file
from sentence_transformers import SentenceTransformer

t1 = time.time()

model = SentenceTransformer("intfloat/e5-base-v2")

db = DataBase()
filt = Filter(db.chapters_dict)
cache = Cache(db_file.cache_path, "v006")

all_q = filt.get()
print(f"Total questions: {len(all_q)}")

# Load existing cache (if any)
cache_key = "EmbeddingsChapters"
if cache.is_cached(cache_key):
    embed_dict = cache.load_cache_pkl(cache_key) or {}
else:
    embed_dict = {}
    cache.creat_cache_pkl(embed_dict, cache_key)

# Map question_id -> question text
q_map = {q.question_id: q.question for q in all_q}

# Find missing ids
missing_ids = [qid for qid in q_map if qid not in embed_dict]
print(f"Missing embeddings: {len(missing_ids)}")

if missing_ids:
    try:
        batch_size = 64
        for i in range(0, len(missing_ids), batch_size):
            batch_ids = missing_ids[i : i + batch_size]
            texts = [q_map[qid] for qid in batch_ids]

            # encode batch with normalization and progress bar
            vectors = model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True,
                normalize_embeddings=True,
            )

            # ensure serializable (lists) before saving
            for qid, vec in zip(batch_ids, vectors):
                embed_dict[qid] = vec.tolist() if hasattr(vec, "tolist") else vec

            # save progress after each batch
            cache.creat_cache_pkl(embed_dict, cache_key)
            print(f"Saved {i + len(batch_ids)} / {len(missing_ids)} new embeddings")

    except KeyboardInterrupt:
        # Save progress on interruption
        cache.creat_cache_pkl(embed_dict, cache_key)
        print("Interrupted — progress saved.")

# Final ensure full cache saved
cache.creat_cache_pkl(embed_dict, cache_key)

t2 = time.time()
print(f"Total time: {t2 - t1:.2f}s")
