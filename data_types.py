import os
from typing import List
from collections import namedtuple
from pydantic import BaseModel, Field
from config import PROJECT_ROOT_DIR


class Parameters(BaseModel):
    clusters_index: str
    answers_index: str
    stopwords_files: List[str]
    max_hits: int
    chunk_size: int
    sbert_score: float
    host: str
    port: int


class SearchData(BaseModel):
    """"""
    pubid: int = Field(title="Пабайди, в котором будет поиск дублей")
    text: str = Field(title="вопрос для поиска")



class TextsDeleteSample(BaseModel):
    """Схема данных для удаления данных по тексту из Индекса"""
    Index: str
    Texts: list[str]
    FieldName: str
    Score: float


ROW = namedtuple("ROW", "SysID, ID, Cluster, ParentModuleID, ParentID, ParentPubList, "
                        "ChildBlockModuleID, ChildBlockID, ModuleID, Topic, Subtopic, DocName, ShortAnswerText")
