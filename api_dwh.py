#       Пример использования функции в коде
#       Получить отчет за 1 месяц для системы Завуч, издание vip, раздел НПД

#       from api_dwh import get_query_doc_report
#       result_df = get_query_doc_report(period=1, sysId=37, pubDivID=3, pubId=183)

#######################################################################################

# описания
# https://jira.action-media.ru/browse/DP-7960
# https://conf.action-media.ru/display/DP/DAG%3A+ss_dm__reports_api

import requests
import pandas as pd
import sys
import os

os.chdir('../Action_scripts/')
sys.path.insert(0, '')
from connect_to_spreadsheet import make_connection

pd.options.display.width = 0
pd.options.mode.chained_assignment = None  # default='warn'
pd.options.display.max_rows = 500

# обращаемся к гугл-доку ДСМ
spreadsheet = make_connection("ДСМ").worksheet("title", "Системы_Издания")
df = spreadsheet.get_as_df()
df = df[~df["Урл на главную версию"].isin(["", "_"])]
sysid_to_sysAlias = dict(df[["sysid", "alias"]].values.tolist())

spreadsheet = make_connection("ДСМ").worksheet("title", "alias_Издания")
df = spreadsheet.get_as_df()
pubid_to_alias = dict(df[["PubId", "алиас издания"]].values.tolist())

spreadsheet = make_connection("ДСМ").worksheet("title", "alias_Разделы")
df = spreadsheet.get_as_df()
pubdivid_to_alias = dict(df[["PubDivID", "alias"]].values.tolist())


def select_sys():
    """Выбираю систему, по которой нужна статистика"""

    print()
    print("Какая систем интересует:")
    for sys_id_, alias_ in sysid_to_sysAlias.items():
        print(sys_id_, "-", alias_)

    sysId = int(input(">>> "))
    print()

    return sysId


def get_query_doc_report(period, sysId, pubDivID=None, pubId=None, save=False):
    """Возвращает датафрейм по отчету 'Запрос - куда переходили'
    Параметры:
    period - период выгрузки. Возможные значения 1,3,6,12
    sysId - номер системы
    pubDivID - раздел поиска (необязательный параметр)
    pubId - издание (необязательный параметр)
    save - Сохранить ли xlsx файл
    """
    pageNumber = 1
    result_df = pd.DataFrame()

    while True:
        url = f"http://ss-statistics-dataplatform.prod.dataplatform.aservices.tech/api/v1/statistics_get-search-link?pageSize=10000&pageNumber={pageNumber}&period={period}&sys={sysid_to_sysAlias[int(sysId)]}"

        if pubDivID:
            url += f"&section={pubdivid_to_alias[pubDivID]}"
        if pubId:
            url += f"&pub={pubid_to_alias[pubId]}"

        headers = {"Content-Type": "application/json"}
        response = requests.request("GET", url, headers=headers)
        df = pd.DataFrame(response.json())

        if len(df) > 0:
            
            # привожу к нижнему регистру
            df['requestStringVariants'] = df['requestStringVariants'].astype(str)
            df['requestStringVariants'] = df['requestStringVariants'].str.lower()

            # ЧИСТКА
            # 1) от запросов с пустой нормальной формой (состоят из стоп-слов)
            df = df[~(df["requestStringNormal"] == "")]
            # 2) от запросов с пустой формой самого запроса (сбой при записи статистики)
            df = df[~(df["requestStringVariants"] == "")]
            # 3) от запросов с пустой формой названия (документ уже удален)
            df = df[~(df["document_name"] == "")]

            result_df = pd.concat([result_df, df], axis=0)
            print("- скачал страницу статистики:", pageNumber)
            pageNumber += 1
        else:
            break

    print()
    print(url)
    print("Длина таблицы до агрегации:", len(result_df))

    result_df = result_df.sort_values("documentId")

    # Агрегируем из-за того, что нормальная форма у одного и того же запроса в разное время может отличаться
    # (ПО documentGroupId ОТДЕЛЬНО НИЧЕГО ДЕЛАТЬ НЕ НАДО - так как стата считается в рамках documentGroupId, а не moduleId).
    # В таком сучае суммируем requestCount и transition_count по ним
    result_df = result_df.groupby(["requestStringVariants", "documentGroupId"]).agg({
        "requestStringNormal": "last",
        "requestCount": "sum",
        "moduleId": "last",
        "documentId": "last",
        "document_name": "last",
        "transition_count": "sum"
    }).reset_index()

    print("Длина таблицы после агрегации:", len(result_df))

    if save == True:
        result_df.to_excel("report.xlsx")
        print("Файл report.xlsx сохранен")

    print(f'Всего в скачанном отчете {len(result_df)} строк')
    return result_df


if __name__ == "__main__":
    period = int(input("Введите период выгрузки. 1,3,6 или 12 месяцев:\n"))
    sysId = select_sys() # int(input("Введите номер системы:\n"))
    result_df = get_query_doc_report(
        period=period,
        sysId=sysId,
        save=False,
    )
    print(result_df)
    