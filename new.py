# ...existing code...
import time, traceback
from core import DataBase,Filter,pdfy

print("START")
start = time.time()
try:
    print("Creating DataBase()...")
    db = DataBase()
    print("DataBase created:", type(db))
    try:
        chapters = getattr(db, "chapters_dict", None)
        print("chapters_dict present:", chapters is not None)
        if hasattr(chapters, "__len__"):
            print("chapters_dict size:", len(chapters))
    except Exception:
        print("error inspecting chapters_dict")
        traceback.print_exc()

    print("Creating Filter...")
    filter = Filter(db.chapters_dict)
    print("Filter created")

    topic = "pressure-density-pascals-law-and-archimedes-principle"
    print("Building query for topic:", topic)
    f = filter.by_topic(topic).by_n_last_yrs(5)
    print("Query built; calling cluster()...")
    cluster = f.cluster()
    try:
        print("cluster type:", type(cluster))
        if hasattr(cluster, "__len__"):
            print("cluster size:", len(cluster))
    except Exception:
        traceback.print_exc()

    print("Rendering...")
    pdfy.render_cluster_to_html(cluster, "pascal_topic_2.html")
    print("Rendered pascal_topic_2.html")
except Exception:
    print("Unhandled exception:")
    traceback.print_exc()
finally:
    print("Elapsed:", time.time()-start)
# ...existing code...