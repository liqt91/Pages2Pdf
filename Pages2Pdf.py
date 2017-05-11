"""
 Page2Pdf基类
~~~~~~~~~~~~~~
爬取目录结构明确的网站，并将其转换到pdf.
需要由子类实现menu_parser()和body_parser()函数
"""

import re
import urllib
import os

import pdfkit
import requests


class Pages2Pdf(object):
    """
    网页转pdf基类
    """
    num_of_instance = 0 #实例化计数器
    def __init__(self,url,name):
        """
        初始化
        """
        self.name = name
        self.start_url = url
        self.domain =  "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
        '''
        urlparse会解析url并返回ParseResult对象，结构如下：
        >>> uri = urlparse('http://www.google.com/search?a=1')
        >>> print(uri)
        ParseResult(scheme='http', netloc='www.google.com',
                    path='/search', params='', query='a=1', fragment='')
        '''
        Pages2Pdf.num_of_instance += 1


    def crawl(self,url):
        """
        返回url的response对象
        @url 网页地址
        :return response
        """
        response = requests.get(url)
        return response


    def menu_parser(self,response):
        """
        目录解析，返回目录对应的url地址列表
        @response: 包含目录的网页内容
        :return 解析后的目录，dict（name, url），建议yield
        """
        return NotImplementedError


    def body_parser(self,response):
        """
        内容解析，对内容设定格式
        @response: 未经格式处理的内容
        :return 经过格式处理的内容
        """
        return NotImplementedError


    @staticmethod
    def create_and_write_file(parent_path,file_name,content=None):
        """
        创建文件
        @parent_path: 文件位置
        @file_name: 文件名
        @content: 写入文件的内容，可以为空
        :return
        """
        if not (parent_path.endswith('/') or file_name.startswith('/')):
            total_path = parent_path + '/' + file_name
        else:
            total_path = parent_path + file_name
        with open(total_path, 'wb') as f:
            if content:
                f.write(content)
            return f


    @staticmethod
    def src_to_path_name(url):
        """
        将url表示的文件转为文件系统的相对路径和文件名
        @url src属性的值
        :return 文件目录和文件名
        """
        image_url = url.split('/')
        if image_url[0]=='':image_url.pop(0)
        if image_url[-1]=='':image_url.pop()
        image_name = image_url.pop()
        image_path = '/'.join(image_url)
        return image_path, image_name


    def run(self,parent_path,pdf_name):
        """
        保存处理过的网页内容并转换为pdf
        @parent_path 文件存储的相对路径，请省略最后一个"/"
        @pdf_name 文件名
        """
        options={
    		'page-size':'Letter',
    		'encoding':'utf-8',
    		'dpi':350, #解决macbookRetina机型字体过小
    		'custom-header':[
    			('Accept-Encoding','gzip')
    		]
    	}
        htmls_name=[]
        for index, url in enumerate(self.menu_parser(self.crawl(self.start_url))):
            html = self.body_parser(self.crawl(url))
            image_partten = '<img.*src="(.*?)"'
            image_urls = re.compile(image_partten).findall(html)
            for image_url in image_urls:
                if image_url.startswith('http'): continue
                image_path,image_name = self.src_to_path_name(image_url)
                try:
                    os.makedirs('htmls/' + image_path)
                except Exception as e:
                    print("Exception:", e)
                image = urllib.request.urlopen(self.domain + image_url)
                self.create_and_write_file('htmls/' + image_path, image_name, image.read())
                # urllib.request.urlretrive(url,image_path + '/' + iamge_name)
            name = '.'.join([str(index),'html'])
            def insert_dot_0(m):
                if not m.group(2).startswith('http'):
                    res = m.group(1) + '.' + m.group(2)
                else:
                    res = m.group(1) + m.group(2)
                return res
            image_partten = '(<img.*src=")(.*?")'
            html = re.compile(image_partten).sub(insert_dot_0,html)
            self.create_and_write_file(parent_path,name,html.encode('utf-8'))
            htmls_name.append(parent_path + '/' + name)
        pdfkit.from_file(htmls_name,pdf_name,options=options)
