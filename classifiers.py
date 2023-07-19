"""
классификатор KNeighborsClassifier в /home/an/Data/Yandex.Disk/dev/03-jira-tasks/aitk115-support-questions
"""
from data_types import Parameters
from storage import ElasticClient
from texts_processing import TextsTokenizer
from config import logger
from sentence_transformers import util
from collections import namedtuple
# https://stackoverflow.com/questions/492519/timeout-on-a-function-call

tmt = float(10)  # timeout


class FastAnswerClassifier:
    """Объект для оперирования MatricesList и TextsStorage"""

    def __init__(self, tokenizer: TextsTokenizer, parameters: Parameters, model):
        self.es = ElasticClient()
        self.tkz = tokenizer
        self.prm = parameters
        self.model = model


    async def tested_searching(self, text: str, pubid: int, score: float, inx_field="LemString"):
        """"""
        """возвращает несколько скоров и позиций эластика для оценки работы Эластик + Сберт:"""
        SearchResult = namedtuple("SearchResult", "Etalon, LemEtalon, TransitionCount, RequestCount, ModuleId, DocumentId, documentGroupId, DocumentName, Score")
        try:
            tokens = self.tkz([text])
            if tokens[0]:
                tokens_str = " ".join(tokens[0])
                etalons_search_result = await self.es.texts_search(self.prm.clusters_index, inx_field, [tokens_str])
                result_dicts = etalons_search_result[0]["search_results"]
                if result_dicts:
                    results_tuples = [(d["requestStringVariants"], d["LemString"], 
                                       d["transition_count"], d["requestCount"], d["moduleId"], d["documentId"], 
                                       d["documentGroupId"], d["document_name"]) for d in result_dicts]
                    text_emb = self.model.encode(text)
                    ets = [x[0] for x in results_tuples]
                    candidate_embs = self.model.encode(ets)
                    scores = util.cos_sim(text_emb, candidate_embs)
                    scores_list = [score.item() for score in scores[0]]
                    search_result = {}
                    candidates = [SearchResult(*(tp + (s, ))) for tp, s in zip(results_tuples, scores_list)]
                    the_best_result = sorted(candidates, key=lambda x: x[8], reverse=True)[0]
                    return the_best_result._asdict()
                else:
                    logger.info("elasticsearch doesn't find any etalons for input text {}".format(str(text)))
                    return SearchResult(*("No", "No", "No", "No", "No", "No", "No", "No", 0))._asdict()
            else:
                logger.info("tokenizer returned empty value for input text {}".format(str(text)))
                return SearchResult(*("No", "No", "No", "No", "No", "No", "No", "No", 0))._asdict()
        except Exception:
            logger.exception("Searching problem with text: {}".format(str(text)))
            return SearchResult(*("No", "No", "No", "No", "No", "No", "No", "No", 0))._asdict()
