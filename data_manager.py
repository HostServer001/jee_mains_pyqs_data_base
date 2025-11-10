import os
import json
import pickle
import time
from sentence_transformers import SentenceTransformer
import pdfy
from sklearn.preprocessing import StandardScaler
import hdbscan
import numpy as np
import datetime as dt

data_base_path = "/home/jvk/CScripts/rev_engine/exam_goal_db"
cache_path = "/home/jvk/CScripts/rev_engine/cache"
schema_version = "v004"
model = SentenceTransformer("all-MiniLM-L6-v2")

class DataBase:
    def __repr__(self):
        return self.name
    def __init__(self,name:str="Data Base")->None:
        """Initializing the data base"""
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
            cache.creat_cache_pkl("DataBaseChapters",chapter_dict)
        
        
        #=====Assigninment of VARS=====
        self.name = name
        self.subject_map = subject_map
        """subject_map is a dict object it return the a direcotry with
        keys as the index of the subjects(same indexes will be used to
        locate the chpaters in the chpaters_list)
        Example:- {0: 'maths', 1: 'phy', 2: 'chem'}
        """
        self.chapters_dict = chapter_dict
        

class Chapter:
    def __repr__(self):
        return self.name
    
    def __init__(self,chapter_path)->None:
        chapter_file = open(chapter_path,"r")
        chapter_json = json.load(chapter_file)
        chapter_file.close()

        parent_subject = chapter_json["results"][0]["title"]
        question_dict = dict()
        counter = 0
        for question_json in chapter_json["results"][0]["questions"]:
            question = Question(question_json)
            question_dict[counter] = question
            counter += 1
        
        self.parent_subject = parent_subject
        self.name = chapter_json["results"][0]["questions"][0]["chapter"]
        self.question_dict = question_dict
        self.total_questions = len(question_dict)

class Question:
    def __repr__(self):
        template = f"""
QuestionId: {self.question_id}
Exam: {self.exam}
Year: {self.year}
Subject: {self.subject}
Chapter: {self.chapter}
"""
        return template
    def __init__(self, question_json: dict) -> None:
        self.question_id = question_json.get("question_id", "")
        self.examGroup = question_json.get("examGroup", "")
        self.exam = question_json.get("exam", "")
        self.subject = question_json.get("subject", "")
        self.chpaterGroup = question_json.get("chapterGroup", "")
        self.chapter = question_json.get("chapter", "")
        self.year = question_json.get("year", 0)
        self.paperTitle = question_json.get("paperTitle", "")
        self.difficulty = question_json.get("difficulty", "")
        self.topic = question_json.get("topic", "")
        self.type = question_json.get("type", "")
        self.examDate = question_json.get("examDate", None)
        self.answer = question_json.get("answer",None)
        question_en = question_json.get("question", {}).get("en", {})
        self.question = question_en.get("content", "")
        self.options = question_en.get("options", {})
        self.correct_options = question_en.get("correct_options", [])
        self.explanation = question_en.get("explanation", "")

        self.isOutOfSyllabus = question_json.get("isOutOfSyllabus", False)
        self.isBonus = question_json.get("isBonus", False)

        
        self.isImgQuestion = self.check_image_in_question()
        self.isImgExplanation = self.check_image_in_explanation()
        self.isImgOption = self.check_image_in_options()
        
        #self.embedding = model.encode(self.question) #disbaled for v003 testing version 

    def check_image_in_question(self)->bool:
        question = self.question
        question_s = question.split("<img")
        if len(question_s) != 1:
            return True
        else:
            return False
    
    def check_image_in_explanation(self)->bool:
        question = self.explanation
        question_s = question.split("<img")
        if len(question_s) != 1:
            return True
        else:
            return False
    
    def check_image_in_options(self)->bool:
        options_json = self.options
        option_bool_list = []
        for option in options_json:
            option_content = option["content"]
            option_content_s = option_content.split("<img")
            if len(option_content_s) != 1:
                option_bool_list.append(True)
            else:
                option_bool_list.append(False)
        return option_bool_list

class Cache:
    def __repr__(self):
        return f"Cache(cache_path='{self.cache_path}',schema_version='{self.schema_version}')"
    
    def __init__(self,cache_path,schema_version):
        self.cache_path = cache_path
        self.schema_version = schema_version
    

    def creat_cache_pkl(self,data_name:str,data_dict:dict)->None:
        time_part = str(time.time()).split(".")[0]
        name_part = data_name
        version_part = self.schema_version

        cache_name = f"{time_part}-{name_part}-{version_part}"
        cache_file_path = os.path.join(self.cache_path,f"{cache_name}.pkl")
        cache_file = open(cache_file_path,"wb")

        pickle.dump(data_dict,cache_file)
    

    def load_cache_pkl(self,data_name:str)->dict:
        cache_file_path = self.cache_path
        cache_files = os.listdir(cache_file_path)
        for file_name in cache_files:
            if file_name.split("-")[1] == data_name and file_name.split("-")[-1] == f"{self.schema_version}.pkl":
                cache_data_path = os.path.join(cache_file_path,file_name)
                cache_file = open(cache_data_path,"rb")
                return pickle.load(cache_file)
    
    def is_cached(self,data_name:str)->bool:
        cache_file_path = self.cache_path
        cache_files = os.listdir(cache_file_path)
        for file_name in cache_files:
            if file_name.split("-")[1] == data_name and file_name.split("-")[-1] == f"{self.schema_version}.pkl":
                return True
        return False
                


class Filter:
    def __init__(self,chapter_class_dict:dict)->None:
        self.chapter_class_dict = chapter_class_dict
        self.filterable_param = self.get_filter_params()
        self.current_set = [
            question
            for chapter in self.chapter_class_dict.values()
            for question in chapter.question_dict.values()
        ]
    
    def reset(self):
        self.current_set = [
            question
            for chapter in self.chapter_class_dict.values()
            for question in chapter.question_dict.values()
        ]
        return self
    
    def get_filter_params(self)->list:
        random_question = self.chapter_class_dict["probability"].question_dict[0]
        param_dict = random_question.__dict__
        return param_dict.keys()
    
    # ...existing code...
    # ...existing code...
    def get_possible_filter_values(self)->dict:
        params = self.get_filter_params()
        possible_values = {}
        if not self.current_set:
            return possible_values

        # Fields that are known to be unique or not useful as filters
        static_skip = {
            "embedding",
            "question",
            "options",
            "question_id",
            "explanation",
            "answer",
            "isImgQuestion",
            "isImgExplanation",
            "isImgOption",
            "correct_options",
        }

        for param in params:
            # always skip static bad fields
            if param in static_skip:
                continue

            seen = {}
            for question in self.current_set:
                val = getattr(question, param, None)
                # create a stable key for unhashable types
                try:
                    # prefer using the raw value when hashable
                    hash(val)
                    key = ("h", val)
                except Exception:
                    try:
                        key = ("j", json.dumps(val, default=str, sort_keys=True))
                    except Exception:
                        key = ("r", repr(val))
                if key not in seen:
                    seen[key] = val

            # If every question has a unique value for this param, skip it
            if len(seen) == len(self.current_set):
                continue

            possible_values[param] = list(seen.values())

        return possible_values
        
    
    def by_year(self,year:int):
        self.current_set = [
            question
            for question in self.current_set if question.year == year
        ]
        return self
    
    def by_subject(self,subject:str):
        self.current_set = [
            question
            for question in self.current_set if question.subject == subject
        ]
        return self
    
    def by_topic(self,topic:str):
        self.current_set = [
            question
            for question in self.current_set if question.topic == topic
        ]
        return self
    
    def by_n_last_yrs(self,n:int):# work in progress
        current_set = []
        current_year = dt.datetime.now().year
        for i in range(n):

            self.by_year()
    
    def by_chapter(self,chapter:str):
        self.current_set = [
            question
            for question in self.current_set if question.chapter == chapter
        ]
        return self

    def get(self):
        return self.current_set
    
    def cluster(self):
        """
        Clusters the current set of questions based on their embeddings using HDBSCAN.
        Returns a dictionary with cluster labels as keys and lists of Question objects as values.
        """
        # Get embeddings for all questions in current set
        embeddings = [question.embedding for question in self.current_set]
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings)
        
        # Scale the embeddings
        scaled = StandardScaler().fit_transform(embeddings_array)
        
        # Run HDBSCAN clustering
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean')
        cluster_labels = clusterer.fit_predict(scaled)
        
        # Create dictionary to store clusters
        clusters = {}
        
        # Group questions by cluster label
        for label, question in zip(cluster_labels, self.current_set):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(question)
        
        return clusters
    
    

"""        
t1 = time.time()
db = DataBase()

filter = Filter(db.chapters_dict)
t2 = time.time()

print(f"Load Time: {t2-t1}")
print(filter.get_possible_filter_values())
"""
db = DataBase()
filter = Filter(db.chapters_dict)
# q_2025 = filter.by_year(2025).by_chapter("basics-of-organic-chemistry").get()
# q_2024 = filter.by_year(2024).get()
# q_2023 = filter.by_year(2023).get()
# q_2022 = filter.by_year(2022).get()
# q_2021 = filter.by_year(2021).get()

def damn():
    for chapter in db.chapters_dict.values():
        last_5_chap_q = []
        for i in range(5):
            filter.reset().by_chapter(chapter)
            questions = filter.by_year(2020+i).get()
            last_5_chap_q.extend(questions)


# questions = filter.by_topic("bohrs-model-and-hydrogen-spectrum").cluster()
# #questions = filter.by_topic("bohrs-model-and-hydrogen-spectrum").by_year(2025).get()
# print(len(questions))
# print(questions.keys())
# pdfy.render_cluster_to_html(questions,"test.html")
