import os
import json
import pandas as pd
from texts_processing import TextsTokenizer
from config import (logger,
                        PROJECT_ROOT_DIR)
from classifiers import FastAnswerClassifier
from sentence_transformers import SentenceTransformer
from data_types import Parameters


with open(os.path.join(PROJECT_ROOT_DIR, "data", "config.json"), "r") as jf:
    config_dict = json.load(jf)

parameters = Parameters.parse_obj(config_dict)

stopwords = []
if parameters.stopwords_files:
    for filename in parameters.stopwords_files:
        root = os.path.join(PROJECT_ROOT_DIR, "data", filename)
        stopwords_df = pd.read_csv(root, sep="\t")
        stopwords += list(stopwords_df["stopwords"])


model = SentenceTransformer(os.path.join(PROJECT_ROOT_DIR, "models", "expbot_paraphrase.transformers"))
tokenizer = TextsTokenizer()
tokenizer.add_stopwords(stopwords)
classifier = FastAnswerClassifier(tokenizer, parameters, model)
logger.info("service started...")