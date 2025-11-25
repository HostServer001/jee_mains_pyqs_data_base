# JEE Mains PYQS Database

![image](https://github.com/HostServer001/jee_mains_pyqs_data_base/blob/main/assets/image.png)

This project provides a structured database of more than 14,000 previous year questions (PYQS) from JEE Mains. The questions are reverse engineered from API endpoints of a subscription site and cached for efficient use. It supports clustering, filtering, and rendering of questions into HTML for easy study.

## Features

* Access to 14k+ JEE Mains PYQS  
* Precomputed embeddings using the `intfloat/e5-large-v2` model for efficient clustering  
* Cluster similar questions together based on semantic embeddings  
* Apply chainable filters (by chapter, topic, year, etc.)  
* Render filtered or clustered questions into HTML using themed styles  

## Project Structure

The core folder contains the following modules:

* **cache.py** – Defines the `Cache` class for creating and loading internal caches. Not intended for direct user interaction.  
* **chapter.py** – Defines the `Chapter` class, which is stored in the `DataBaseChapters` cache file. Internal use only.  
* **data_base.py** – Defines the `DataBase` class. This must be initialized before any operations.  
* **filter.py** – Defines the `Filter` class. Provides chainable methods to filter questions and update the current set.  
* **question.py** – Defines the `Question` object.  
* **styles.py** – Contains themed HTML styles for rendering.  
* **pdfy.py** – Provides functions to convert clusters or sets of questions into HTML.  

## Installation

* **Install using pip**:
* Install the package
```
pip install jee_data_base
```

* Install chromium 
```plawright install chromium```

* **Clone the repository**:

```
git clone https://github.com/HostServer001/jee_mains_pyqs_data_base
```

Navigate into the project directory and ensure dependencies are installed.

## Usage

### Basic Initialization

```python
import os
from jee_data_base import DataBase, Filter, pdfy

# Initialize database
db = DataBase()

# Initialize filter
filter = Filter(db.chapters_dict)

# Inspect available chapters
print(filter.get_possible_filter_values()["chapter"])
```
**Its highly recommended to filter as much as possible so that your html files open smoothly in browser**

**Its always good to use the ```cluster``` method and ```render_cluster_to_html``` method to get your output, it provides the most efficeint way of practice**

**The ```render_cluster_to_html_skim``` is great if you have prepared chapter loosely and want to skin thorugh and get most out of it (use it after ```cluster```)**

### Most useful feature

```python
from jee_data_base import DataBase,Filter
import asyncio

path = "<path where chpater folder will be created>"
chpater = "<your example chpater>"

#Load the data base
db = DataBase()

#Initialize filter
filter = Filter(db.chapter_dict)

#Create html file
asyncio.run(filter.render_chap_last5yrs(path,chpater,skim=False,output_file_format="pdf"))
```

### Filtering by Chapter and Year

```python
# Get all questions from a specific chapter in the last 3 years
questions = filter.by_chapter("thermodynamics").by_n_last_yrs(3).get()

for q in questions:
    print(q.question)
```

### Clustering and Rendering

```python
# Cluster questions by topic and render to HTML
filter.current_set = filter.by_chapter("organic-compounds").by_n_last_yrs(5).get()
cluster = filter.cluster()

pdfy.render_cluster_to_html(
    cluster,
    "organic_compounds.html",
    "Organic Compounds - Last 5 Years"
)# can use render_cluster_to_html_skim() function to make a file which 
#makes a html file perfected for skiming through a chapter
```

### Example: Render Chapter Questions by Topic

```python
def render_chapter(chapter_name: str):
    all_q = filter.by_chapter(chapter_name).by_n_last_yrs(5).get()
    os.makedirs(chapter_name, exist_ok=True)

    for topic in filter.get_possible_filter_values()["topic"]:
        filter.current_set = all_q
        filter.by_topic(topic)
        cluster = filter.cluster()
        pdfy.render_cluster_to_html_skim(
            cluster,
            f"{chapter_name}/{topic}.html",
            topic
        )

render_chapter("alcohols-phenols-and-ethers")
```

## Ouput

* The output will look somthing like this
[PDF 📄](assets/pdf-file.pdf)

## Data Caches

* **DataBaseChapters** – Contains a dictionary with chapter names as keys and `Chapter` objects as values.  
* **EmbeddingsChapters** – Contains precomputed embeddings of all questions to save computation time.  

## Contributing

Contributions are welcome. You can help by:

* Improving documentation  
* Adding new filters or clustering strategies  
* Enhancing rendering styles  
* Reporting issues and suggesting features  

Fork the repository, create a new branch for your changes, and submit a pull request.

## License

This project is provided for educational purposes. Please review the repository for licensing details.
