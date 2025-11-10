"""
This file has the DataBase class.
"""


import os
from core.cache import Cache
from core.chapter import Chapter


data_base_path = ""
cache_path = ""
schema_version = "v006"
"""
-data_base_path is absolute path to examgoal database
-cache_path is absolute path to cache
-schema_version is used to keep track of versioning the cache
                cauese newer version may inculde some additional data
                in the elemntal form of this database that is Question class
                the older cache in that case will become incompatible with the
                new system. On every new schema update the schema version will change
                this ensures DataBase loads properly with new version and cache 
                created accordingly
"""


class DataBase:
    """
    This class adds a layer of abstration to access the examgoal database
    """
    def __repr__(self)->str:
        """
        For text output pourposes
        """
        template = f"""
Name: {self.name}
Total Chapters: {len(self.chapters_dict)}
State: {self.state}
"""
        return template
    
    def __init__(self,name:str="Data Base")->None:
        """Initializing the DataBase"""
        cache = Cache(cache_path=cache_path,schema_version=schema_version)

        subjects = os.listdir(data_base_path)
        subject_map = {i:subjects[i] for i in range(len(subjects))}
        
        if cache.is_cached("DataBaseChapters"):
            chapter_dict = cache.load_cache_pkl("DataBaseChapters")
        else:
            chapter_dict = dict()
            
            for subject in subjects:
                sub_chapters_list = os.listdir(
                    os.path.join(
                        data_base_path,
                        subject
                        )
                    )
                for chap_name in sub_chapters_list:
                    try:
                        chap_class = Chapter(
                            os.path.join(
                                data_base_path,
                                subject,
                                chap_name
                            )
                        )
                        chap_name_str = chap_name.split(".")[0]
                        chapter_dict[chap_name_str] = chap_class
                    except KeyError as e:
                        print(f"{chap_name} cant load:  {e}")
            cache.creat_cache_pkl(data_name="DataBaseChapters",data_dict=chapter_dict)
        
        
        self.name = name
        self.subject_map = subject_map #dict
        self.chapters_dict = chapter_dict
        self.state = "healthy"