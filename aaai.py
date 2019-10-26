# -*- coding: utf-8 -*-
"""
A simple crawler for AAAI

Created on Jul 07 19:40:53 2019

@author: G.Q.
"""

import os
import re

import lxml
import requests
from lxml import etree


class AAAIDownloader:
    def __init__(self, year, key_word, folder_prefix, summary_path):
        self.key_word = key_word
        self.summary_path = summary_path
        self.year = self.process_year(year)
        self.information = ''.join(['Event : AAAI', ', Year : ', str(year), ', Keyword : ', self.key_word])
        self.enter_url = 'http://www.aaai.org/Library/AAAI/aaai' + self.year + 'contents.php'
        self.target_file_folder = folder_prefix + '/AAAI' + str(year)
        self.result = self.get_result()

    @staticmethod
    def process_year(year):
        if not isinstance(year, int):
            raise ValueError('Year must be integer.')
        if 1980 <= year <= 1999:
            return str(year % 1900)
        elif 2000 <= year <= 2019:
            return str(year % 2000)
        else:
            raise ValueError('Year is not in valid range.')

    @staticmethod
    def get_pdf_url(tag_lst):
        pdf_url = None
        for i in range(len(tag_lst)):
            if isinstance(tag_lst[i], lxml.etree._Element):
                if 'href' in tag_lst[i].attrib:
                    pdf_url = tag_lst[i].attrib['href']
        return pdf_url

    def get_result(self):
        print(self.information)
        response = requests.get(self.enter_url)
        if response.status_code != 200:
            print("Status code : ", response.status_code)
            return []
        content = etree.HTML(response.text)
        node_list = content.xpath('//p[@class=\'left\']')
        resources = []
        for node in node_list:
            paper_title = node.xpath('string(.)').split('/')[0].strip().split('\n')[0].strip()
            tags = node.xpath('node()')
            paper_url = self.get_pdf_url(tags)
            download_url = re.sub('view', 'download', paper_url)
            resources.append((download_url, paper_title))
        if self.key_word == '' or None:
            return resources
        else:
            return list(filter(lambda x: (self.key_word.lower() in x[1].lower()), resources))

    def download(self):
        if not self.result:
            print('There is no paper associate with keywords.')
            return None
        if not os.path.exists(self.target_file_folder):
            os.makedirs(self.target_file_folder)
        for index, (download_url, title) in enumerate(self.result):
            binary_result = requests.get(download_url)
            with open(self.target_file_folder + '/' + re.sub('''[<>/:|"*?]''', ' ', title) + '.pdf', 'wb') as file:
                file.write(binary_result.content)
            print('No.', index + 1, 'Download success :', title)

    def write_summary(self):
        with open(self.summary_path, 'a+', encoding='utf-8') as summary_file:
            if not self.result:
                print('There is no data to write summary.')
                return None
            summary_file.write(self.information + '\n')
            for url, title in self.result:
                summary_file.write(title + ' ' + '\n')
            summary_file.write('\n')
        print('Summary write success.')


if __name__ == '__main__':
    years = [2019, 2018]
    keywords = ['multi-task']
    downloader = None
    for y in years:
        for k in keywords:
            downloader = AAAIDownloader(y, k, './paper_aaai_others', './summary_aaai_others.txt')
            # downloader.download()
            downloader.write_summary()
