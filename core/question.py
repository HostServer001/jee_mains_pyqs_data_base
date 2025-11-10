"""
This file has Question class
"""

from sentence_transformers import SentenceTransformer

class Question:
    """Loads data from database into inherited class variables"""
    def __repr__(self)->str:
        template = f"""
QuestionId: {self.question_id}
Exam: {self.exam}
Year: {self.year}
Subject: {self.subject}
Chapter: {self.chapter}
"""
        return template
    def __init__(self, question_json: dict,embedding_model:str="all-MiniLM-L6-v2") -> None:
        """Initialization of Question
        :param:
        question_json: json part of question (this is kind of hardcoded configured to examgoal database
                        and the structure of this system)
        embedding_model: A vail SentenceTransformer embedding model name . default to all-MiniLM-L6-v2
        """
        #model = SentenceTransformer(embedding_model)

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

        
        self.isImgQuestion = self.check_image_in_text(self.question)
        self.isImgExplanation = self.check_image_in_text(self.explanation)
        self.isImgOption = self.check_image_in_options()
        
        #self.embedding = model.encode(self.question) #disbaled for v003 testing version | this is a computation
        #heavy param will take 8 mins to calc the embeddings | latest update moving embeddings to its seprate cache!!!

    def check_image_in_text(self,text:str)->bool:
        """Check if text consists of image (inform of html)"""
        text_s = text.split("<img")
        if len(text_s) != 1:
            return True
        else:
            return False
    
    def check_image_in_options(self)->bool:
        """Check if question consists of image (inform of html)"""
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