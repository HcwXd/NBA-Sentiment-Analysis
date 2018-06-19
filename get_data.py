import requests
import time
import re
import jieba
import codecs

from bs4 import BeautifulSoup


war_match_dict = ["勇士", "咖哩", "柯瑞", "Curry", "KD",
                  "嘴綠", "Klay", "杜蘭特", "Green", "KT", "格林", "湯森", "我勇"]
cav_match_dict = ["騎士", "詹姆士", "詹姆斯", "姆斯", "詹皇", "LBJ", "LeBron",
                  "James", "Korver", "Jeff", "JR", "Smith",  "Cavs", "Lue", "史密斯", "Love", "詹", "我騎", "Hill"]

jieba.add_word((s) for s in war_match_dict)
jieba.add_word((s) for s in cav_match_dict)


def is_related(title):
    war_related = False
    cav_related = False
    if any(re.search(s, title, re.IGNORECASE) for s in war_match_dict):
        war_related = True
    if any(re.search(s, title, re.IGNORECASE) for s in cav_match_dict):
        cav_related = True

    if(war_related and cav_related):
        return "BOTH"
    elif (war_related):
        return "WAR"
    elif(cav_related):
        return "CAVS"
    else:
        return False


def get_data(start_month, start_day, end_month, end_day):
    BOARD_NAME = "NBA"
    url = 'https://www.ptt.cc/bbs/' + BOARD_NAME + '/index.html'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    max_index = soup.find_all('a', 'btn wide')
    previous_page = max_index[1].get('href')
    previous_index = int(previous_page.split('index')[1].split('.')[0])
    articles = soup.find_all('div', 'r-ent')

    # index = previous_index+1
    index = 5983
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
                if(is_related(title)):
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
                # else:
                #     print("no the title is "+title)

        if(break_point):
            break
        index -= 1
        is_first_page = False


def word_frequecy(text):
    frequency = {}
    seg_list = jieba.cut(contents_collection[0], cut_all=False)
    for word in seg_list:
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1
    return frequency


titles_collection = []
contents_collection = []
comments_collection = []

get_data(6, 1, 6, 4)

# for title in titles_collection:
#     print(title)
#     seg_list = jieba.cut(title, cut_all=False)
#     print("/ ".join(seg_list))
apple = word_frequecy(contents_collection)
print(apple)
