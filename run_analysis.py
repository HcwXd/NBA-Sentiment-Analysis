import requests
import time
import re
import jieba
import statistics

from bs4 import BeautifulSoup


war_match_dict = ["勇士", "咖哩", "柯瑞", "K湯", "Curry", "CURRY", "curry", "KD", "kd", "嘴綠", "Klay", "durant", "Durant",
                  "kerr", "ai", "AI", "McGee", "杜蘭特", "Green", "green", "KT", "kt", "格林", "湯森", "我勇", "浪花", "四巨頭", "四星"]
cav_match_dict = ["騎士", "詹姆士", "喇叭", "詹姆斯", "姆斯", "詹皇", "LBJ", "lbj", "LeBron", "lebron", "James", "james", 'tt', "TT",
                  "Korver", "Jeff", "JR", "jr", "丁尺", "smith", "皇", "我皇", "Smith",  "Cavs", "Lue", "史密斯", "Love", "詹", "我騎", "Hill"]


def add_word_to_jieba(word_collection):
    for word in word_collection:
        jieba.add_word(word)


add_word_to_jieba(war_match_dict)
add_word_to_jieba(cav_match_dict)


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
    index = 6006
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


def team_label(word_frequency, title):
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

    if any(re.search(s, title, re.IGNORECASE) for s in war_match_dict):
        war_score += 5
    if any(re.search(s, title, re.IGNORECASE) for s in cav_match_dict):
        cav_score += 5

    output.write("\ncav_score: "+str(cav_score) +
                 " / war_score: "+str(war_score)+"\n")

    if(cav_score > war_score):
        return "CAV"
    elif(cav_score < war_score):
        return "WAR"
    else:
        return "EQ"


def count_score(text, team):
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
    pos = []
    neg = []
    for word in seg_list:
        if word in poslist:
            pos.append(word)
        elif word in neglist:
            neg.append(word)
    output.write("\n=======================POSITIVE===================\n")
    output.write(str(len(pos))+"\n")
    for x in pos:
        output.write(x+"/ ")
    output.write("\n=======================NEGATIVE===================\n")
    output.write(str(len(neg))+"\n")
    for x in neg:
        output.write(x+"/ ")

    point_table = []
    for x in range(4):
        point_table.append(0)

    if(team == "WAR"):
        points = len(pos)-len(neg)
        point_table[0] += points
        if(points > 0):
            point_table[1] += 1
        elif(points < 0):
            point_table[1] -= 1
    elif(team == "CAV"):
        points = len(pos)-len(neg)
        point_table[2] += points
        if(points > 0):
            point_table[3] += 1
        elif(points < 0):
            point_table[3] -= 1
    return point_table


for game_index in range(4):
    index = game_index+1

    titles_collection = []
    contents_collection = []
    comments_collection = []

    cav_total_points = 0
    war_total_points = 0

    cav_good_posts = 0
    war_good_posts = 0

    cav_total_posts = 0
    war_total_posts = 0

    cav_points_collection = []
    war_points_collection = []

    game_date = ["5/29", "6/1", "6/4", "6/7", "6/9"]
    data_date = ["5/31", "6/3", "6/6", "6/8"]

    get_data(game_date[game_index], data_date[game_index])

    for i in range(len(titles_collection)):
        file_name = './game'+str(index)+'/No.'+str(i)+".txt"
        output = open(file_name, 'w+')

        output.write("=======================TITLE======================\n")
        output.write(titles_collection[i])

        output.write("\n=======================CONTENT====================\n")
        seg = jieba.cut(contents_collection[i], cut_all=False)
        output.write("/ ".join(seg))

        output.write("\n=======================LABEL======================\n")
        team = team_label(word_frequecy(
            contents_collection[i]), titles_collection[i])
        if(team == "WAR"):
            war_total_posts += 1
        elif(team == "CAV"):
            cav_total_posts += 1
        output.write(team)
        point_table = count_score(contents_collection[i], team)
        output.close()

        war_total_points += point_table[0]
        war_good_posts += point_table[1]
        cav_total_points += point_table[2]
        cav_good_posts += point_table[3]

        war_points_collection.append(point_table[0])
        cav_points_collection.append(point_table[2])

    file_name = './game'+str(index)+'/predict.txt'
    output = open(file_name, 'w+')

    output.write("======================CAV_STAT======================\n")
    output.write("Total posts:\t "+str(cav_total_posts)+"\n")
    # output.write("Good post:\t\t " +
    #              str((cav_good_posts+cav_total_posts)/2)+"\n")
    # output.write("Bad post:\t\t " +
    #              str((cav_total_posts - cav_good_posts)/2)+"\n")
    output.write("Post scores:\t "+str(cav_good_posts)+"\n")

    output.write("Total points:\t "+str(cav_total_points)+"\n")
    output.write("Best points:\t "+str(max(cav_points_collection)))
    output.write("   \tat post No." +
                 str(cav_points_collection.index(max(cav_points_collection)))+"\n")
    output.write("Worst points:\t "+str(min(cav_points_collection)))
    output.write("   \tat post No." +
                 str(cav_points_collection.index(min(cav_points_collection)))+"\n")
    output.write(
        "Stdev:\t\t\t "+str(statistics.stdev(cav_points_collection))+"\n")

    output.write("======================WAR_STAT======================\n")
    output.write("Total posts:\t "+str(war_total_posts)+"\n")
    # output.write("Good post:\t\t " +
    #              str((war_good_posts+war_total_posts)/2)+"\n")
    # output.write("Bad post:\t\t " +
    #              str((war_total_posts - war_good_posts)/2)+"\n")
    output.write("Post scores:\t "+str(war_good_posts)+"\n")

    output.write("Total points:\t "+str(war_total_points)+"\n")
    output.write("Best points:\t "+str(max(war_points_collection)))
    output.write("   \tat post No." +
                 str(war_points_collection.index(max(war_points_collection)))+"\n")
    output.write("Worst points:\t "+str(min(war_points_collection)))
    output.write("   \tat post No." +
                 str(war_points_collection.index(min(war_points_collection)))+"\n")
    output.write(
        "Stdev:\t\t\t "+str(statistics.stdev(war_points_collection))+"\n")
    output.close()
