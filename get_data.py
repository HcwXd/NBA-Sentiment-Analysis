import requests
import time
from bs4 import BeautifulSoup

PAGES = 1
BOARD_NAME = "NBA"

NOT_EXIST = BeautifulSoup('<a>本文已被刪除</a>', 'lxml').a

url = 'https://www.ptt.cc/bbs/' + BOARD_NAME + '/index.html'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

max_index = soup.find_all('a', 'btn wide')
previous_page = max_index[1].get('href')
previous_index = int(previous_page.split('index')[1].split('.')[0])
articles = soup.find_all('div', 'r-ent')

index = previous_index+1
is_first_page = True
break_point = False


titles_collection = []
contents_collection = []
comments_collection = []

while(True):
    time.sleep(0.01)
    url = 'https://www.ptt.cc/bbs/'+BOARD_NAME+'/index'+str(index)+'.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.find_all('div', 'r-ent')

    for article in articles:
        print("---------------------")
        meta = article.find('div', 'title').find('a')
        if meta == None:
            continue
        else:
            title = meta.getText().strip()
            link = meta.get('href')
            date = article.find('div', 'date').getText()
            print(date)
            split_date = date.split('/')

            if not(is_first_page):
                if(int(split_date[0]) < 6):
                    break_point = True
                    break
                if(int(split_date[0]) == 6 and int(split_date[1]) < 19):
                    break_point = True
                    break

            response = requests.get(
                "https://www.ptt.cc"+link)
            soup = BeautifulSoup(response.text, 'lxml')
            post = soup.find('div', 'bbs-screen bbs-content')

            if(post.contents[4]):
                titles_collection.append(title)
                contents_collection.append(post.contents[4])
                comments = soup.find_all('div', 'push')
                c = []
                for comment in comments:
                    c.append(comment.getText())
                comments_collection.append(c)
    if(break_point):
        break
    index -= 1
    is_first_page = False
