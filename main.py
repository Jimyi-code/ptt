import time
import requests
import pandas
import sys
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
load_dotenv()

# 常數
# 目標網址
TARGET_URL = "https://www.ptt.cc/bbs/"

# 目標看板
target_board = "Tech_Job"

#目標頁面
TARGET_PAGE = "/index"

#目標頁數
page_num = ""

#頁面附屬檔名
PAGE_EXT = ".html"

target = TARGET_URL + target_board + TARGET_PAGE + page_num  + PAGE_EXT

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}

#data = requests.get(target, headers = headers)
#print(data.content)

def download_html(target, headers):    
    return requests.get(target, headers= headers)

def parser_board_urls(requests_):
    html_code = BeautifulSoup(requests_.content)
    div_list = html_code.find_all('div', class_="title")
    
    urls = []
    for div_ in div_list:
        try:
            a_tag = div_.find('a').attrs['href']
        except:
            a_tag = None
        urls.append(a_tag)
    return urls

def parser_article_content(url_list):
    ptt_data = []
    for url_ in url_list:
        if url_ != None:
            article_url = 'https://www.ptt.cc' + url_
            page_data = download_html(article_url, HEADERS)
            page_html_code = BeautifulSoup(page_data.content, features="html.parser")
            try:
                article_data = page_html_code.find_all('span', class_="article-meta-value")
                article_author = article_data[0].contents[0]
                article_title = article_data[2].contents[0]
                article_time = article_data[3].contents[0]
                article_body = page_html_code.find('div', id='main-content').contents[4]
                article_row = {
                    'url': article_url,
                    'title': article_title,
                    'author': article_author,
                    'time': article_time,
                    'content': article_body
                }
                ptt_data.append(article_row)
            except:
                print("parser error:", article_url)
   
    time.sleep(1)
    return ptt_data

# function Test
#a = download_html(target, headers)
#b = parser_board_urls(a)
#c = parser_article_content(b)
#print(c)

##Test
#a = download_html(target, headers)
#print(a.content)

def export_json(data):
    ptt_df = pandas.DataFrame(data)
    ptt_df.to_json("ptt.json")
    return True

## Test
#a = download_html(target, headers)
#b = parser_board_urls(a)
#c = parser_article_content(b)
#export_json(c)
#print(c)

import datetime
def main():
    
    # 目標看板
    target_board = "Tech_Job"
    
    #目標頁數
    page_num = ""
    
    target = TARGET_URL + target_board + TARGET_PAGE + page_num  + PAGE_EXT
    
    
    print("接收參數的長度", len(sys.argv))
    if len(sys.argv) < 2:
        print("缺少參數: 爬蟲的目標看板！")
        sys.exit()
    if len(sys.argv) == 2:    
        page_num == ""
        print("未偵測到目標頁數，因此只進行最新文章頁面進行爬蟲")
    else:
        #---main code---#
        #print("參數內容(list):", sys.argv)
        #print("印出第一個參數:", sys.argv[0])
        #print("印出第二個參數:", sys.argv[1])
        
        target_board = sys.argv[1]
        
        page_num = sys.argv[2]
        #合併目標網址
        target = TARGET_URL + target_board + TARGET_PAGE + page_num  + PAGE_EXT
        print(target) 
        
        # 爬蟲執行順序
        # download_html() -> parser_board_urls() -> parser_article_content() -> export_json()
           
        # download_html: arg1: 網址, arg2: 請求標頭, returns: requests class
        # parser_board_urls: arg1: request class, returns: (list) urls
        # parser_article_content: arg1: (list) urls, return: (list) ppt_data
        # export_json: arg1: (list) ppt_data, return: (Boolean) True, Output: ppt.json
           
        

        
         #---main code---#
         
        res = download_html(target, HEADERS)
        url_list = parser_board_urls(res)
        ptt_data = parser_article_content(url_list)
        export_json(ptt_data)
        print(ptt_data)

        time_str = "{date:%Y-%m-%d %H:%M%S}".format(date = datetime.datetime.now())
        process_st = send_line_notify("{} - 看板爬蟲已完成".format(time_str, target_board))
        if process_st == 200:
            print("Line Notify 通知完成。")
        else:
            print("Line Notify API Error")
               
        return None



import json
def send_line_notify (msg = "Send message"):
    line_notify_url = "https://notify-api.line.me/api/notify"
    line_notify_token = os.getenv("Token")
    
    #Line Auth Headers
    line_notify_header = {
        'Authorization': 'Bearer {}'.format(line_notify_token)
    }
   
    # Line Message
    line_notify_body = {
        'message':  msg
    }
   
    res = requests.post(line_notify_url, headers=line_notify_header, data = line_notify_body)
    res_msg =  json.loads(res.text)


    return res_msg['status']

send_line_notify('You cannot kill me')
# 加入 __main__ 執行區段
if __name__ == '__main__':
 main()


#from dotenv import dotenv_values
#config = dotenv_values(".env")
#print(config['Test'])