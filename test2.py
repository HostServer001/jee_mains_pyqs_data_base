from jee_data_base import DataBase,Filter
import asyncio

path = ""
chpater = "alcohols-phenols-and-ethers"

#Load the data base
db = DataBase()

#Initialize filter
filter = Filter(db.chapters_dict)

#Create html file
asyncio.run(filter.render_chap_lastNyrs(destination=path,chap_name=chpater,skim=False,output_file_format="pdf"))
