"""
继承实现了pages2pdf类，爬取廖雪峰的python课程并转换为pdf
~~~~~~~~~~~~~~~~~~~~

"""

from Pages2Pdf import Pages2Pdf
from bs4 import BeautifulSoup

class LXFPythonTutorial2Pdf(Pages2Pdf):
    """
    爬取廖雪峰的python课程并转换为pdf
    """
    html_template = """
        <html>
            <head></head>
            <body>
                {0}
            </body>
        </html>
    """
    def menu_parser(self,response):
        soup = BeautifulSoup(response.content,'html.parser')
        menu = soup.find_all(class_='uk-nav uk-nav-side')[1]
        for li in menu.find_all('li'):
            url = li.a.get('href')
            if not url.startswith('http'):
                url = self.domain + url
            # yield li.a.string, url
            yield url


    def body_parser(self,response):
        soup = BeautifulSoup(response.content,"html.parser")
        x_wiki_content = soup.find_all(class_='x-wiki-content')[0]
        h4 = soup.find(class_='x-content').find('h4')
        title = soup.new_tag('h1')
        title.string = h4.string
        center_title = soup.new_tag('center')
        center_title.insert(1,title)
        x_wiki_content.insert(1,center_title)
        html = LXFPythonTutorial2Pdf.html_template.format(x_wiki_content)
        return html


start_url = 'http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000'
def main():
    lxf = LXFPythonTutorial2Pdf(start_url,'lxfpythontutorial2pdf')
    # for name,url in lxf.menu_parser(lxf.crawl(lxf.start_url)):
    #     print("name:",name)
    #     print("url:",url)
    lxf.run("htmls","pythontutorial.pdf")


if __name__ == '__main__':
    main()
