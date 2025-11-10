"""
This file has the Cache class
"""

import os
import time
import pickle
import importlib

class Cache:
    """Handels cache creation ,loading and checking"""
    def __repr__(self)->str:
        template = f"""
Cache Path: {self.cache_path}
Schema Version: {self.schema_version}
"""
        return template
    
    def __init__(self,cache_path,schema_version):
        """Initialization of Cache
        :param: 
        cache_path: Path to cache folder (it's recommended to use absolute path)
        schema_version: Which version of schema Cache is supposed to handel
        """
        self.cache_path = cache_path
        self.schema_version = schema_version
    

    def creat_cache_pkl(self,data_dict:dict,data_name:str = "DataBaseChapters")->None:
        """Create a cache
        :param:
        data_name: name part of the cache
        data_dict: dict to create cache of
        """
        time_part = str(time.time()).split(".")[0]
        name_part = data_name
        version_part = self.schema_version

        cache_name = f"{time_part}-{name_part}-{version_part}"
        cache_file_path = os.path.join(self.cache_path,f"{cache_name}.pkl")
        cache_file = open(cache_file_path,"wb")

        pickle.dump(data_dict,cache_file)
    

    def load_cache_pkl(self,data_name:str)->dict:
        """Loads the cache safely into any code
        resolves the pickel load issue by itself
        :param:
        data_name: name part of the cache
        """
        cache_file_path = self.cache_path
        cache_files = os.listdir(cache_file_path)
        for file_name in cache_files:
            parts = file_name.split("-")
            if len(parts) < 3:
                continue
            if parts[1] == data_name and parts[-1] == f"{self.schema_version}.pkl":
                cache_data_path = os.path.join(cache_file_path,file_name)
        
                class _FixUnpickler(pickle.Unpickler):#this part is vibe coded lol
                    def find_class(self, module, name):
                        # remap classes pickled under "__main__" into their core modules
                        if module == "__main__":
                            # try a heuristic: core.<lowercase class name> first
                            try:
                                mod = importlib.import_module(f"core.{name.lower()}")
                                #print(mod)
                                return getattr(mod, name)
                            except Exception:
                                # fallback explicit mapping for known moved classes
                                mapping = {
                                    "Chapter": "core.chapter",
                                    "Question": "core.question",
                                    # add other class-name -> module mappings here as needed
                                }
                                if name in mapping:
                                    module = mapping[name]
                        return super().find_class(module, name)

                with open(cache_data_path,"rb") as file:
                    return _FixUnpickler(file).load()

        raise FileNotFoundError(f"No cache file for '{data_name}' (schema {self.schema_version})")
    
    def is_cached(self,data_name:str)->bool:
        """Check if the data is cached and also checks the schema version
        :param:
        data_name: name part of the cache
        """
        cache_file_path = self.cache_path
        cache_files = os.listdir(cache_file_path)
        for file_name in cache_files:
            if file_name.split("-")[1] == data_name and file_name.split("-")[-1] == f"{self.schema_version}.pkl":
                return True
        return False