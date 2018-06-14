import requests
import time
from bs4 import BeautifulSoup

PAGES = 20
BOARD_NAME = "NBA"
CONDITION = 50

NOT_EXIST = BeautifulSoup('<a>本文已被刪除</a>', 'lxml').a

url = 'https://www.ptt.cc/bbs/' + BOARD_NAME + '/index.html'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

max_index = soup.find_all('a', 'btn wide')
previous_page = max_index[1].get('href')
previous_index = int(previous_page.split('index')[1].split('.')[0])
articles = soup.find_all('div', 'r-ent')

index = previous_index+1
break_point = False
is_first_page = True

while(True):
    time.sleep(0.01)
    url = 'https://www.ptt.cc/bbs/'+BOARD_NAME+'/index'+str(index)+'.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.find_all('div', 'r-ent')
    print(index)

    for article in articles:
        meta = article.find('div', 'title').find('a')
        if meta == None:
            continue
        else:
            title = meta.getText().strip()
            link = meta.get('href')
            push = article.find('div', 'nrec').getText()
            date = article.find('div', 'date').getText()
            author = article.find('div', 'author').getText()
            if push == "" or push[0] == "X":
                push = 0
            if push == "爆":
                push = 9999
            split_date = date.split('/')
            if not(is_first_page):
                if(int(split_date[0]) < 6):
                    break_point = True
                    break
                if(int(split_date[0]) == 6 and int(split_date[1]) < 12):
                    break_point = True
                    break
    index -= 1
    is_first_page = False
    if(break_point):
        break
