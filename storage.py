"""https://elasticsearch-py.readthedocs.io/en/latest/async.html"""
import asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from config import (logger, 
                    es_url,
                    es_user,
                    es_pass)
# from data_types import ElasticSettings


# setting = ElasticSettings()
class ElasticClient(AsyncElasticsearch):
    """Handling with AsyncElasticsearch"""
    
    def __init__(self, *args, **kwargs):
        # self.settings = ElasticSettings()
        self.loop = asyncio.new_event_loop()
        super().__init__(
            hosts=es_url,
            basic_auth=(es_user, es_pass),
            request_timeout=100,
            max_retries=50,
            retry_on_timeout=True,
            *args,
            **kwargs,
        )

    async def texts_search(self, index: str, searching_field: str, texts: list[str]) -> list:
        async def search(tx: str, field: str):
            resp = await self.search(
                allow_partial_search_results=True,
                min_score=0,
                index=index,
                query={"match": {field: tx}},
                size=100,
            )
            return resp

        texts_search_result = []
        for txt in texts:
            res = await search(txt, searching_field)
            if res["hits"]["hits"]:
                texts_search_result.append(
                    {
                        "text": txt,
                        "search_results": [
                            {
                                **d["_source"],
                                **{"id": d["_id"]},
                                **{"score": d["_score"]},
                            }
                            for d in res["hits"]["hits"]
                        ],
                    }
                )
        return texts_search_result

    def delete_index(self, index_name) -> None:
        """Deletes the index if one exists."""

        async def delete(index: str):
            """
            :param index:
            """
            try:
                await self.indices.delete(index=index)
                await self.close()
            except:
                await self.close()
                logger.info("impossible delete index with name {}".format(index_name))

        try:
            self.loop.run_until_complete(delete(index_name))
        except:
            logger.info("It is impossible delete index with name {}".format(index_name))
    
    def add_docs(self, index_name: str, docs: list[dict]):
        """
        :param index_name:
        :param docs:
        """

        async def add(index: str, dcs: list[dict]):
            """Adds documents to the index."""
            _gen = (
                {
                    "_index": index,
                    "_source": doc
                } for doc in dcs
            )
            await async_bulk(self, _gen, chunk_size=50, stats_only=True)
            await self.close()

        try:
            self.loop.run_until_complete(add(index_name, docs))
            logger.info("adding {} documents in index {}".format(len(docs), index_name))
        except Exception:
            logger.exception("Impossible adding {} documents in index {}".format(len(docs), index_name))
