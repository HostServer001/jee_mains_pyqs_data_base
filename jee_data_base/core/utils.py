import re
import os
from . import cache_path
from pathlib import Path
from .data_base import schema_version
from requests import Session
from tqdm import tqdm

session = Session()

def check_cache_health(data_name:str)->bool:
    pattern = rf"\d*-{data_name}-{schema_version}.pkl"

    cache_files_paths = os.listdir(cache_path)
    cache_files = [Path(file).name for file in cache_files_paths]
    health = False
    for i in cache_files:
        if re.search(pattern,i):
            health = True
    return health

def download_cache(data_name:str)->None:
    pattern = rf"\d*-{data_name}-{schema_version}.pkl"
    for i in range(5):
        try:    
            cache_file_dict = _get_release_files_dict()
            break
        except Exception as e:
            print(e)
    if cache_file_dict == None:
        return None            
    for i in cache_file_dict.keys():
        if re.search(pattern,i):
            response = session.get(cache_file_dict[i], stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 65536

            file_path = cache_path/i
            with open(file_path, 'wb') as file, tqdm(
                total=total_size, unit='B', unit_scale=True, desc=str(file_path)
            ) as progress_bar:
                for data in response.iter_content(block_size):
                    file.write(data)
                    progress_bar.update(len(data))


def _get_release_files_dict(owner:str="HostServer001", repo:str="jee_mains_pyqs_data_base")->dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    response = session.get(
        url,
        verify=False
        )
    releases = response.json()
    asset_dict = {}
    for asset in releases[0]["assets"]:
        asset_dict[asset["name"]] = asset["browser_download_url"]
    
    return asset_dict

