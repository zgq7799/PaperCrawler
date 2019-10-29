# -*- coding: utf-8 -*-
"""
A simple crawler for ACL

Created on Jul 07 14:44:05 2019

@author: G.Q.
"""

import os
import re

import requests
from lxml import etree


class ACLDownloader:
    def __init__(self, event, year, key_word, folder_prefix, summary_path):
        self.url_prefix = 'https://www.aclweb.org/anthology/events/'
        self.download_prefix = 'https://www.aclweb.org/anthology/'
        self.key_word = key_word
        self.summary_path = summary_path
        self.information = ''.join(['Event : ', event, ', Year : ', year, ', Keyword : ', key_word])
        self.enter_url = self.url_prefix + event.lower() + '-' + year
        self.target_file_folder = folder_prefix + '/' + event + year
        self.result = self.get_result()

    def get_result(self):
        print(self.information)
        response = requests.get(self.enter_url)
        if response.status_code != 200:
            print("Status code : ", response.status_code)
            return []
        content = etree.HTML(response.text)
        node_list = content.xpath('//p/span/strong/a[@class=\'align-middle\']')
        resources = []
        for node in node_list:
            paper_code = node.xpath('@href')[0].strip().split('/')[-2]
            paper_title = node.xpath('string(.)').strip()
            resources.append((paper_code, paper_title))
        if self.key_word == '' or self.key_word is None:
            return resources
        else:
            return list(filter(lambda x: (self.key_word.lower() in x[1].lower()), resources))

    def download(self):
        if not self.result:
            print('There is no paper associate with keywords.')
            return None
        if not os.path.exists(self.target_file_folder):
            os.makedirs(self.target_file_folder)
        for index, (code, title) in enumerate(self.result):
            download_url = self.download_prefix + code + '.pdf'
            binary_result = requests.get(download_url)
            with open(self.target_file_folder + '/' + re.sub('''[<>/:|"*?]''', ' ', title) + '.pdf', 'wb') as file:
                file.write(binary_result.content)
            print('No.', index + 1, 'Download success :', code, title)

    def write_summary(self):
        with open(self.summary_path, 'a+', encoding='utf-8') as summary_file:
            if not self.result:
                print('There is no data to write summary.')
                return None
            summary_file.write(self.information + '\n')
            for code, title in self.result:
                summary_file.write(code + ' ' + title + ' ' + '\n')
            summary_file.write('\n')
        print('Summary write success.')


if __name__ == '__main__':
    events = ['ACL', 'CL', 'CoNLL', 'EACL', 'EMNLP', 'NAACL', 'SEMEVAL', 'TACL', 'WS', 'ALTA', 'COLING', 'IJCNLP',
              'LREC', 'PACLIC', 'RANLP', 'ROCLING-IJCLCLP']
    years = ['2019','2018']
    keywords = ['multi-task']
    downloader = None
    for y in years:
        for e in events:
            for k in keywords:
                downloader = ACLDownloader(e, y, k, './paper_acl_others', './summary_acl_others.txt')
                #downloader.download()
                downloader.write_summary()
