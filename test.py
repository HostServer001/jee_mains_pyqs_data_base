import os
from core import DataBase,Filter,pdfy

data_base_path = "/storage/emulated/0/db_01/jee_mains_pyqs_data_base"
cache_path = f"{data_base_path}/cache"

db = DataBase(data_base_path,cache_path)

filter = Filter(db.chapters_dict)
print(filter.get_possible_filter_values()["chapter"])
"""all_q = []
for i in range(5):
    filter.reset()
    all_q.extend(filter.by_topic("pressure-density-pascals-law-and-archimedes-principle").by_year(2021+i).get())

filter.current_set = all_q
"""

def render_chap_last5yrs(chap_name:str):
    all_q = filter.by_chapter(chap_name).by_n_last_yrs(5).get()
    os.mkdir(chap_name)
    print(filter.get_possible_filter_values()["topic"])
    for topic in filter.get_possible_filter_values()["topic"]:
        filter.current_set = all_q
        filter.by_topic(topic)
        cluster = filter.cluster()
        pdfy.render_cluster_to_html_skim(
            cluster,
            f"{chap_name}/{topic}.html",
            topic
        )

render_chap_last5yrs("alcohols-phenols-and-ethers")

# pdfy.render_cluster_to_html(
#     filter.by_topic("pressure-density-pascals-law-and-archimedes-principle")
#     .by_n_last_yrs(5)
#     .cluster(),
#     "pascal_topic_2.html"
#     )