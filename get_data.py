import requests
import time
from bs4 import BeautifulSoup


def get_data(start_month, start_day, end_month, end_day):
    BOARD_NAME = "NBA"
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

    while(True):
        time.sleep(0.01)
        url = 'https://www.ptt.cc/bbs/'+BOARD_NAME+'/index'+str(index)+'.html'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.find_all('div', 'r-ent')

        for article in articles:
            meta = article.find('div', 'title').find('a')
            if meta == None:
                continue
            else:
                title = meta.getText().strip()
                link = meta.get('href')
                date = article.find('div', 'date').getText()
                split_date = date.split('/')

                if not(is_first_page):
                    if(int(split_date[0]) < start_month):
                        break_point = True
                        break
                    if(int(split_date[0]) == start_month and int(split_date[1]) < start_day):
                        break_point = True
                        break
                    if(int(split_date[0]) > end_month):
                        continue
                    if(int(split_date[0]) == end_month and int(split_date[1]) > end_day):
                        continue
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


titles_collection = []
contents_collection = []
comments_collection = []

get_data(6, 1, 6, 4)

print(titles_collection[0])
print(comments_collection[0][0])
