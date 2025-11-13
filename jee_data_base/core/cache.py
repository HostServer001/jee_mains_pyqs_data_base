"""
This file has the Cache class
"""

import os
import time
import pickle
import importlib
from pathlib import Path

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
        cache_file_paths = os.listdir(cache_file_path)
        cache_files = [Path(file).name for file in cache_file_paths]
        for file_name in cache_files:
            parts = file_name.split("-")
            if len(parts) < 3:
                continue
            if parts[1] == data_name and parts[-1] == f"{self.schema_version}.pkl":
                cache_data_path = os.path.join(cache_file_path,file_name)
        
                class _FixUnpickler(pickle.Unpickler):
                    def find_class(self, module, name):
                        print("Unpickling:", module, name)  # debug

                        # Handle bare "__main__"
                        if module == "__main__":
                            try:
                                mod = importlib.import_module(f"jee_data_base.core.{name.lower()}")
                                return getattr(mod, name)
                            except Exception:
                                mapping = {
                                    "Chapter": "jee_data_base.core.chapter",
                                    "Question": "jee_data_base.core.question",
                                }
                                if name in mapping:
                                    mod = importlib.import_module(mapping[name])
                                    return getattr(mod, name)

                        # Handle "core.*" modules
                        if module.startswith("core."):
                            # Example: "core.chapter" → "jee_data_base.core.chapter"
                            new_module = f"jee_data_base.{module}"
                            try:
                                mod = importlib.import_module(new_module)
                                return getattr(mod, name)
                            except Exception as e:
                                print("Remap failed:", new_module, name, e)
                                raise

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
        cache_file_paths = os.listdir(cache_file_path)
        cache_files = [Path(file).name for file in cache_file_paths]
        for file_name in cache_files:
            if file_name.split("-")[1] == data_name and file_name.split("-")[-1] == f"{self.schema_version}.pkl":
                return True
        return False