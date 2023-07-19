import os
import pandas as pd
from storage import ElasticClient
from texts_processing import TextsTokenizer
from config import PROJECT_ROOT_DIR

def scv2es(es: ElasticClient, file_name: str):
    """обновление данных в индексе "clusters" из csv файлов"""
    data_df = pd.read_csv(os.path.join(PROJECT_ROOT_DIR, "data", file_name), sep="\t")
    queries = list(data_df["requestStringVariants"])
    tknz = TextsTokenizer()
    lm_queries = [" ".join(x) for x in tknz(queries)]
    lm_queries_df = pd.DataFrame(lm_queries, columns=["LemString"])
    data_with_lm_df = pd.concat([data_df, lm_queries_df], axis=1)
    data_with_lm_df.fillna('', inplace=True)
    etalons_for_es = data_with_lm_df.to_dict(orient="records")
    es.delete_index("etalons_for_testing")
    # добавление вопросов и ответов:
    es.add_docs("etalons_for_testing", etalons_for_es)

if __name__ == "__main__":
    es = ElasticClient()
    # es.delete_index("etalons_for_testing")
    scv2es(es, "etalons.csv")