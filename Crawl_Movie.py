# -*- coding: utf-8 -*-
'''
This document aims at crawling movies from some forums and based on the name of movie searching Douban to catch the score;
then selecting out movies which scores are higher than a number user setted, and save them to a txt document to make it convenient
for us to select movies which have high scores.
'''
import sys
import re
import urllib
import urllib2
import cookielib
from bs4 import BeautifulSoup  # using beautiful soup library
from operator import itemgetter # sort movies by Douban score
reload(sys)
sys.setdefaultencoding("utf-8")
# This document taking RS as an example
DOMAIN = u'http://rs.xidian.edu.cn/'
# replace it with your username
USERNAME = u'username'
# replace it with your password
PASSWORD = u'password'
# address of the forum
HOMEURL = DOMAIN + u'forum.php'
# login in address
LOGINURL = DOMAIN + u'member.php?mod=logging&action=login&loginsubmit=yes&handlekey=login&loginhash=LCaB3&inajax=1'
# class of operates to forum, mainly containing login in forum
class Forum(object):
    def __init__(self):
        self.operate = ''
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        urllib2.install_opener(self.opener)
    def response(self, url, data=None):
        if data is not None:
            req = urllib2.Request(url, urllib.urlencode(data))
        else:
            req = urllib2.Request(url)

        response = self.opener.open(req)
        return response
    def login(self, username, password):
        postdata = {
            'username': username,
            'password': password,
            'referer' : 'http://rs.xidian.edu.cn/'
        }
        # obtain information whether success or failure
        self.operate = self.response(LOGINURL, postdata)
        login_page = self.operate.read()
        # display information of login
        if 'succeedhandle_login' in login_page:
            print 'SUCCESS'
            return True
        else:
            print 'FAIL'
        return False
# Class of processing movies. Getting movie lists from forum, and searching scores from Douban, Then sort results based on scores
class Movie():
    # All movies saved in movie_list
    def __init__(self):
        self.movie_list = []
    # extract the precise movie name.
    def extract_movie_name(self, str1):
        list = str1.split('[')
        if list[3][0:-1].isdigit():
            name = list[4]
        else:
            name = list[3]

        if name.find('/') < name.find(']'):
            name = name[0:name.find('/')]
        else:
            name = name[0:name.find(']')]
        return name
    # searching Douban to find the score of movies
    def douban_score(self, url):
        # print url
        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError, e:
            print e.reason
            return 0
        html = response.read()
        soup = BeautifulSoup(html)
        # print html
        scores = soup.select("[class~=rating_nums]")
        if scores.__len__() != 0:
            score_str = str(scores[0])
        else:
            score_str = ''
        b = re.compile(r"(\d+)\.(\d)")
        # print score_str.__sizeof__(), score_str, b.match(score_str[26:29]).group()
        if score_str.__sizeof__() == 57 and b.match(score_str[26:29]):
            score = b.match(score_str[26:29]).group()
        else:
            score = 0
        return score
   # finding movie list in forum(movie name, movie link)
    def start(self, html):
        soup = BeautifulSoup(html)
        html_tbody = soup.find_all('tbody')

        for tbody in html_tbody:
            soup_tmp = BeautifulSoup(str(tbody))
            herf = soup_tmp.find('tbody').find('tr').find('td', class_='common').find('a').get('href')
            name_tmp = soup_tmp.find('tbody').find('tr').find('td', class_='common').find('a').get_text()
            movie_name = self.extract_movie_name(name_tmp)

            score = self.douban_score(
                u'http://movie.douban.com/subject_search?search_text=' + movie_name + u'&cat=1002') # Douban address
            # You can change Douban score threshold to search better movies
            if float(score) > 5.0:
                each_movie = (movie_name, score, DOMAIN + herf[2:])
                self.movie_list.append(each_movie)
    #save the results
    def write_result(self):
        self.movie_list.sort(key=itemgetter(1), reverse=True)
        output = open('data.txt', 'w')
        for tup in self.movie_list:
            str = tup[0] + '|' + tup[1] + '|' + '[' + tup[2] + ']'
            str1 = str.encode('gbk')
            output.write(str1)
            output.write('\n')
        output.close()

# test file
my_account = Forum()
my_account.login(USERNAME, PASSWORD)
movie = Movie()
for page in range(1, 3):
    #this can be changed by you, for you can search more pages
    rs_html = my_account.response('http://rs.xidian.edu.cn/bt.php?mod=browse&c=10&page=' + str(page))
    movie.start(rs_html)
movie.write_result()




