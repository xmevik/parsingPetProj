from bs4 import BeautifulSoup
import requests
from datetime import datetime
from multiprocessing import Pool
import pandas as pd
from parser_class import Parser
from generator import Generator

"""
Помощник по API Habr'a https://habr.com/ru/post/490820/
"""
async def get_html(url: str) -> str:
    """
    Вытягивание html файла страницы
    url: Коенчный путь к сайту
    """
    try:
        html = await requests.get(url, verify=False)
    except Exception as e:
        print(e)
    if(html.status_code != 200):
        print("Ошибка получения страницы, код ошибки: " + html.status_code)
    return html.text

def dataDump(data: pd.DataFrame, fileName: str) -> None:
    try:
        data.to_csv(fileName, mode='a', header=False, index=False)
    except Exception as e:
        print(e)

async def parseCompanyData(href):
    url = Generator(href).generateCompanyProfile()
    html_context = await get_html(url)
    data = Parser(html_context=html_context)
    companyData = data.findCompanyData()
    print('Данные по компании найдены')
    dataDump(companyData, 'companyData.csv')
    print('Данные о компании сохранены')
    data.parseCompanyBlogs()
    print('Данные о компании были получены')


def worker(i):
    companies_url = Generator(i).generateCompaniesPage()
    html_context = get_html(url=companies_url)
    all_arcticles_href = Parser(html_context=html_context, isBlog=False).find_arcticles()
    pool = Pool(5)
    pool.map_async(parseCompanyData, all_arcticles_href)

if __name__ == "__main__":
    pool = Pool(2)
    pool.map(worker, range(1,17))