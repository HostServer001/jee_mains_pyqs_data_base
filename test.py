import os
from core import DataBase,Filter,pdfy
db = DataBase()

filter = Filter(db.chapters_dict)

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
        pdfy.render_cluster_to_html(
            cluster,
            f"{chap_name}/{topic}.html",
            topic
        )

render_chap_last5yrs("haloalkanes-and-haloarenes")

# pdfy.render_cluster_to_html(
#     filter.by_topic("pressure-density-pascals-law-and-archimedes-principle")
#     .by_n_last_yrs(5)
#     .cluster(),
#     "pascal_topic_2.html"
#     )