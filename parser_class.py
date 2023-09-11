from bs4 import BeautifulSoup
import requests
from datetime import datetime
from multiprocessing import Pool
import pandas as pd
from generator import Generator

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

class Parser():
    def __init__(self, html_context: str = None, isBlog: bool = True, *args, **kwargs) -> None:
        self.html_context = html_context
        self.isBlog = isBlog

    def findPagination(self) -> int:
        soup = BeautifulSoup(self.html_context, 'lxml')

        paginations = soup.select('tm-pagination__page')

        if len(paginations) > 0:
            return paginations[-1].text
        else: return 1

    def find_arcticles(self) -> list[str]:
        """
        Парсер для нахождения статей и копированием их ссылок
        html_context: Страница html в строковом представлении
        """
        soup = BeautifulSoup(self.html_context, 'lxml')

        arcticle_class = 'tm-article-snippet__title-link' if self.isBlog else 'tm-article-snippet__title'

        try:
            all_arcticles = soup.find_all('a', class_=arcticle_class)
        except Exception as e:
            print("При обработке этой страници произошла ошибка. Ошибка: " + e)

        self.all_arcticles_href: list = []
        for elem in all_arcticles:
            self.all_arcticles_href.append(elem.get('href'))

        return self.all_arcticles_href
    
    def findCompanyData(self) -> pd.DataFrame:
        soup = BeautifulSoup(self.html_context, 'lxml')

        companyName = soup.find(class_='tm-company-card__name router-link-exact-active router-link-active').get_text()
        description = soup.find(class_='tm-description-list__body tm-description-list__body tm-description-list__body_variant-base').get_text()
        shortDesc = soup.find(class_='tm-company-card__description').get_text()
        rating = soup.find(class_='tm-votes-lever__score-counter tm-votes-lever__score-counter tm-votes-lever__score-counter_rating').get_text()
        self.companyBlogLink = soup.find('a', class_='tm-company-card__name router-link-exact-active router-link-active').get('href').replace('profile', 'blog')
        self.companyName = companyName

        companyData: pd.DataFrame = pd.DataFrame.columns('companyName', 'description', 'shortDesc', 'rating')
        companyData.companyName = companyName
        companyData.description = description
        companyData.shortDesc = shortDesc
        companyData.rating = rating
        
        return companyData
    
    async def findBlogData(self, href) -> None:
        url = Generator(pageNumber=href).generateBlog()
        html_context = await get_html(url)

        soup = BeautifulSoup(html_context, 'lxml')

        try:
            companyName = self.companyName
            title = soup.find('h1', class_='tm-article-snippet__title tm-article-snippet__title_h1').get_text()
            time = soup.find('span',class_='tm-article-snippet__datetime-published').find('time').get('datetime')
            time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
            text = soup.find(class_='post-content-body').get_text()
        except Exception as e:
            print('Произошла ошибка при парсинге блога, ошибка: ' + e)
            print(f'Ссылка на блог {url}')

        data = pd.DataFrame.columns('companyName', 'title', 'time', 'text')

        data.companyName = companyName
        data.title = title
        data.time = time
        data.text = text

        dataDump(data, 'blogData.csv')
        print(f'Блог компании {self.companyName} сохранен')

    async def parseBlogs(self, i):
        url = Generator(pageNumber=i, companylink=self.companyBlogLink).generateCompanyPage()
        html_context = await get_html(url)

        all_arcticles_href = Parser(html_context, isBlog=True).find_arcticles()

        pool = Pool(5)
        pool.map_async(Parser(self.companyName).findBlogData, all_arcticles_href)
    
    async def parseCompanyBlogs(self) -> None:
        url = Generator(companylink=self.companyBlogLink).generateCompanyPage()
        html_context = await get_html(url)
        lastPagination = Parser(html_context).findPagination()

        pool = Pool(2)
        pool.map_async(Parser(companyBlogLink=self.companyBlogLink, companyName=self.companyName).parseBlogs, range(1,lastPagination))