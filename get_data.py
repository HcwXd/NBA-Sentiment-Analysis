import requests
import time
import re
import jieba
import codecs

from bs4 import BeautifulSoup


war_match_dict = ["勇士", "咖哩", "柯瑞", "K湯", "Curry", "CURRY", "curry", "KD", "kd", "嘴綠", "Klay", "durant", "Durant",
                  "kerr", "ai", "AI", "McGee", "杜蘭特", "Green", "green", "KT", "kt", "格林", "湯森", "我勇", "浪花", "四巨頭", "四星"]
cav_match_dict = ["騎士", "詹姆士", "詹姆斯", "姆斯", "詹皇", "LBJ", "lbj", "LeBron", "lebron", "James", "james", 'tt', "TT",
                  "Korver", "Jeff", "JR", "jr", "丁尺", "smith", "皇", "我皇", "Smith",  "Cavs", "Lue", "史密斯", "Love", "詹", "我騎", "Hill"]


def add_word_to_jieba(word_collection):
    for word in word_collection:
        jieba.add_word(word)


add_word_to_jieba(war_match_dict)
add_word_to_jieba(cav_match_dict)
# jieba.add_word((s) for s in war_match_dict)
# jieba.add_word((s) for s in cav_match_dict)


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


def get_data(start_date, end_date):
    start_month, start_day = (start_date.split("/"))
    end_month, end_day = (end_date.split("/"))

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
        aaarrr = 0
        for article in articles:
            aaarrr += 1
            if(aaarrr > 20):
                break_point = True
                break
            meta = article.find('div', 'title').find('a')
            if meta == None:
                continue
            else:
                title = meta.getText().strip()
                link = meta.get('href')
                date = article.find('div', 'date').getText()
                split_date = date.split('/')

                if not(is_first_page):
                    if(int(split_date[0]) < int(start_month)):
                        break_point = True
                        break
                    if(int(split_date[0]) == int(start_month) and int(split_date[1]) < int(start_day)):
                        break_point = True
                        break
                    if(int(split_date[0]) > int(end_month)):
                        continue
                    if(int(split_date[0]) == int(end_month) and int(split_date[1]) > int(end_day)):
                        continue
                if(is_related(title)):
                    response = requests.get(
                        "https://www.ptt.cc"+link)
                    soup = BeautifulSoup(response.text, 'lxml')
                    post = soup.find('div', 'bbs-screen bbs-content')

                    if(re.search("※ 發信站", post.contents[5].getText())):
                        titles_collection.append(title)
                        contents_collection.append(post.contents[4])
                        print("==============================================")
                        print(title)
                        print("https://www.ptt.cc"+link)
                        print(post.contents[4])
                        print("==============================================")
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
    seg_list = jieba.cut(text, cut_all=False)
    for word in seg_list:
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1
    return frequency


def team_label(word_frequency):
    cav_score = 0
    war_score = 0
    output.write("CAV_TERM\n")
    for word in cav_match_dict:
        if word in word_frequency:
            output.write(word+"/ ")
            cav_score += word_frequency[word]
    output.write("\nWAR_TERM\n")
    for word in war_match_dict:
        if word in word_frequency:
            output.write(word + "/ ")
            war_score += word_frequency[word]
    output.write("\ncav_score: "+str(cav_score) +
                 " / war_score: "+str(war_score)+"\n")
    if(cav_score > war_score):
        return "CAV"
    elif(cav_score < war_score):
        return "WAR"
    else:
        return "EQ"


def count_score(text):
    seg_list = jieba.cut(text, cut_all=False)
    poslist = []
    posfile = open('./dict/NTUSD_positive_utf8.txt', 'r')
    for aline in posfile:
        aline = aline.strip()
        poslist.append(aline)
    posfile.close()

    neglist = []
    negfile = open('./dict/NTUSD_negative_utf8.txt', 'r')
    for aline in negfile:
        aline = aline.strip()
        neglist.append(aline)
    negfile.close()

    # print(text)

    pos = [x for x in seg_list if x in poslist]
    neg = [x for x in seg_list if x in neglist]
    output.write("\n=======================POSITIVE===================\n")
    output.write(str(len(pos))+"\n")
    for x in pos:
        output.write(x+"/ ")
    output.write("\n=======================NEGATIVE===================\n")
    output.write(str(len(neg))+"\n")
    for x in neg:
        output.write(x+"/ ")


titles_collection = []
contents_collection = []
comments_collection = []

get_data("6/1", "6/4")

for i in range(10):
    file_name = './game1/No.'+str(i)+".txt"
    output = open(file_name, 'w+')
    output.write("=======================TITLE======================\n")
    output.write(titles_collection[i])
    output.write("\n=======================CONTENT====================\n")
    seg = jieba.cut(contents_collection[i], cut_all=False)
    output.write("/ ".join(seg))
    output.write("\n=======================LABEL======================\n")
    output.write(team_label(word_frequecy(contents_collection[i])))
    count_score(contents_collection[i])
    output.close()

# for title in titles_collection:
#     print(title)
#     seg_list = jieba.cut(title, cut_all=False)
#     print("/ ".join(seg_list))
# count_score(contents_collection[2])
# count_score(contents_collection[3])
