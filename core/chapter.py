"""
This file has the Chapter class
"""

import json
from core.question import Question

class Chapter:
    """Abstraction for chapter"""
    def __repr__(self)->str:
        template = f"""
Parent Subject:{self.parent_subject}
Name:{self.name}
Question Dict: {self.question_dict_status}
Total Questions:{self.total_questions}
"""
        return template
    
    def __init__(self,chapter_path)->None:
        """Initialization of Chapter
        :param:
        chapter_path: Path to chpaters json file , recommended to use absolute path
        """
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
        self.question_dict_status = "healthy"
        self.total_questions = len(question_dict)