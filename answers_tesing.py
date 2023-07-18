import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("URL")

sign = True
pageNumber = 1
pageSize = 10000
period = 1
sys = "bss"

results_df = pd.DataFrame()
while sign:
    parameters="pageSize={}&pageNumber={}&period={}&sys={}".format(str(pageSize), str(pageNumber), str(period), str(sys))
    url = "".join([URL, parameters])
    response = requests.get(url)

    if response.json():
        qrs_df = pd.DataFrame(response.json())
        results_df = pd.concat([results_df, qrs_df]) 
        pageNumber += 1    
    else:
        sign = False
    
results_df.to_csv(os.path.join("data", "queries.csv"), sep="\t", index=False)