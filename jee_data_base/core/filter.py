"""
This file has Filter class
"""
import os
import json
from pathlib import Path
import hdbscan
import numpy as np
import datetime as dt
from typing import Self
from .cache import Cache
from . import cache_path,schema_version
from .pdfy import render_cluster_to_html_skim,render_cluster_to_html
#from core.data_base import cache_path,schema_version
#from sklearn.preprocessing import StandardScaler


class Filter:
    def __init__(self,chapter_class_dict:dict)->None:
        self.chapter_class_dict = chapter_class_dict
        self.filterable_param = self.get_filter_params()
        cache = Cache(cache_path,schema_version)
        self.embeddings_dict = cache.load_cache_pkl("EmbeddingsChapters")
        self.current_set = [
            question
            for chapter in self.chapter_class_dict.values()
            for question in chapter.question_dict.values()
        ]
    
    def reset(self)->Self:
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
    
    def get_possible_filter_values(self)->dict:
        params = self.get_filter_params()
        possible_values = {}
        if not self.current_set:
            return possible_values

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

            if len(seen) == len(self.current_set):
                continue

            possible_values[param] = list(seen.values())

        return possible_values
        
    
    def by_year(self,year:int)->Self:
        self.current_set = [
            question
            for question in self.current_set if question.year == year
        ]
        return self
    
    def by_subject(self,subject:str)->Self:
        self.current_set = [
            question
            for question in self.current_set if question.subject == subject
        ]
        return self
    
    def by_topic(self,topic:str)->Self:
        self.current_set = [
            question
            for question in self.current_set if question.topic == topic
        ]
        return self
    
    def by_n_last_yrs(self,n:int)->Self:
        current_scope = self.get()
        last_n_pyqs = []
        current_year = dt.datetime.now().year
        for i in range(n):
            self.current_set = current_scope
            nth_year = self.by_year(current_year-i).get()
            last_n_pyqs.extend(nth_year)
        self.current_set = last_n_pyqs
        return self

    
    def by_chapter(self,chapter:str)->Self:
        self.current_set = [
            question
            for question in self.current_set if question.chapter == chapter
        ]
        return self
     
    def by_difficulty(self,difficulty:str)->Self:
        self.current_set = [
            question
            for question in self.current_set if question.difficulty == difficulty
        ]
        return self

    def get(self)->list:
        return self.current_set
    
    def render_chap_last5yrs(self,destination:str,chap_name:str,skim:bool=True)->None:
        all_q = self.by_chapter(chap_name).by_n_last_yrs(5).get()
        os.mkdir(str(Path(destination)/chap_name))
        print(self.get_possible_filter_values()["topic"])
        for topic in self.get_possible_filter_values()["topic"]:
            file_path = str(Path(destination)/chap_name/f"{topic}.html")
            self.current_set = all_q
            self.by_topic(topic)
            cluster = self.cluster()
            if skim:
                render_cluster_to_html_skim(
                    cluster,
                    file_path,
                    topic
                )
            else:
                render_cluster_to_html(
                    cluster,
                    file_path,
                    topic
                )

    def cluster(self)->dict:
        """
        Cluster the current set of questions using their vector embeddings.

        Detailed behavior and steps:
        1. Purpose
           - Group similar questions (from self.current_set) into clusters using HDBSCAN
             on precomputed embeddings stored in self.embeddings_dict.
           - The method returns a dictionary mapping cluster labels -> list of Question objects.

        2. Inputs and prerequisites
           - self.current_set: list of Question objects to cluster.
           - self.embeddings_dict: a mapping from question_id -> embedding (iterable of floats).
           - Each embedding must be indexable by question.question_id and be convertible to a numeric
             numpy array.

        3. High-level steps
           a) Collect embeddings for questions in self.current_set.
              - Questions missing an embedding are skipped from the clustering step and collected
                separately under the 'missing_embedding' key in the result.
           b) If there are fewer than MIN_SAMPLE_SIZE embeddings available, HDBSCAN is not run.
              - In that case, all available embedding-backed questions are labeled as noise (label -1).
           c) Otherwise, run HDBSCAN on the embeddings array to compute cluster labels.
              - HDBSCAN parameters:
                - min_cluster_size: controls the minimum size of a cluster (set by MIN_SAMPLE_SIZE).
                - metric: euclidean (sensible default for dense embeddings).
              - HDBSCAN assigns a label -1 to points considered noise (not belonging to any persistent cluster).
           d) Build and return a dict mapping labels -> lists of Question objects in that cluster.
              - The returned dict includes:
                - integer cluster labels produced by HDBSCAN (including -1 for noise).
                - a 'missing_embedding' entry (string key) for questions that had no embedding available.

        4. Notes and design choices
           - We avoid failing when some questions lack embeddings; they are separated out instead.
           - The method does not modify embeddings or apply dimensionality reduction by default.
             If scaling or dimensionality reduction is desired, enable and apply it before calling HDBSCAN
             or modify this method to perform scaling (e.g., StandardScaler) / PCA/UMAP.
           - HDBSCAN requires more than one sample to form clusters in a meaningful way; hence the
             MIN_SAMPLE_SIZE guard.

        5. Return value
           - dict: { label -> [Question, ...], ..., 'missing_embedding': [Question, ...] }
             Example:
               {
                 -1: [Question(...), ...],         # noise by HDBSCAN
                  0: [Question(...), Question(...)],
                  1: [Question(...), ...],
                  'missing_embedding': [Question(...), ...]  # optional
               }
        """
        MIN_SAMPLE_SIZE = 2

        if not self.current_set:
            return {}

        # Collect embeddings for questions that have them; keep track of missing ones
        embeddings = []
        questions_with_embeddings = []
        missing_embedding_questions = []

        for question in self.current_set:
            emb = self.embeddings_dict.get(question.question_id)
            if emb is None:
                missing_embedding_questions.append(question)
                continue
            embeddings.append(emb)
            questions_with_embeddings.append(question)

        # No embeddings available at all
        if not embeddings:
            result = {}
            if missing_embedding_questions:
                result["missing_embedding"] = missing_embedding_questions
            return result

        embeddings_array = np.array(embeddings)

        # If too few samples to cluster, mark all as noise (-1)
        if len(embeddings) < MIN_SAMPLE_SIZE:
            clusters = {-1: list(questions_with_embeddings)}
            if missing_embedding_questions:
                clusters["missing_embedding"] = missing_embedding_questions
            return clusters

        # Run HDBSCAN
        clusterer = hdbscan.HDBSCAN(min_cluster_size=MIN_SAMPLE_SIZE, metric="euclidean")
        cluster_labels = clusterer.fit_predict(embeddings_array)

        # Group questions by cluster label
        clusters = {}
        for label, question in zip(cluster_labels, questions_with_embeddings):
            clusters.setdefault(label, []).append(question)

        # Attach missing-embedding questions if any
        if missing_embedding_questions:
            clusters["missing_embedding"] = missing_embedding_questions

        return clusters
# ...existing code...