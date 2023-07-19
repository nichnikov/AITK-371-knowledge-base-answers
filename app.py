""""""
import os
import uvicorn
from fastapi import FastAPI
from start import (classifier, 
                       parameters)
from config import logger
from data_types import SearchData

os.environ["TOKENIZERS_PARALLELISM"] = "false"
app = FastAPI(title="ExpertBotFastText")


@app.post("/api/search")
# @timeit
async def search(data: SearchData):
    """searching etalon by  incoming text"""
    logger.info("searched pubid: {} searched text: {}".format(str(data.pubid), str(data.text)))
    logger.info("searched text without spellcheck: {}".format(str(data.text)))
    result = await classifier.tested_searching(str(data.text), data.pubid, parameters.sbert_score)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host=parameters.host, port=parameters.port)
