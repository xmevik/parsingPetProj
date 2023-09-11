class Generator():
    def __init__(self, pageNumber = None, companylink = None) -> None:
        self.__page = pageNumber
        self.__companyLink = companylink

    def generateCompanyProfile(self) -> str:
        url = f'https://habr.com{self.__companyLink}'
        return url
    
    def generateCompaniesPage(self) -> str:
        url = f'https://habr.com/ru/companies/page{self.__page}'
        return url
    
    def generateCompanyPage(self) -> str:
        url = f'https://habr.com/{self.__companyLink}/page{self.__page}'
        return url
    
    def generateBlog(self) -> str:
        url = f'https://habr.com{self.__page}'
        return url