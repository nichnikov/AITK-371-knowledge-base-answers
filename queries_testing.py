import os
import pandas as pd
import requests

queies_df = pd.read_csv(os.path.join("data", "test_queries.csv"), sep="\t")
print(queies_df)
queies_dicts_list = queies_df.to_dict(orient="records")
test_results = []
for num, d in enumerate(queies_dicts_list):
    q = d["Query"]
    print(num, q)
    q_request = {"pubid": 9, "text": q}
    res = requests.post("http://0.0.0.0:8090/api/search", json=q_request)
    res_dict = res.json()
    res_dict["Query"] = q
    test_results.append({**d, **res_dict})

print(test_results)
test_results_df = pd.DataFrame(test_results)
print(test_results_df)
test_results_df.to_csv(os.path.join("data", "test_results.csv"), sep="\t", index=False)