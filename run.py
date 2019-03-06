import requests
import datetime
import itchat
from bs4 import BeautifulSoup
import demjson
import re
import signal
import sys
import time

exf_name = './ex.json'

urls = [ # interested group urls
    'https://www.douban.com/group/?????/',
]

def quit(signalnum, frame):
    print('----------------EXIT----------------')
    itchat.logout()
    sys.exit()

def is_good(title):
    # filter of interested topic, most important!
    return re.search('广州|GZ|gz|羊城|粤',title)


def main():
    itchat.auto_login(enableCmdQR=2)
    try:
        ex = demjson.decode_file(exf_name)
    except (demjson.JSONDecodeError, FileNotFoundError):
        ex = list()
    
    exl = [e['user'] for e in ex]

    soups = []
    for url in urls:
        soups.append(BeautifulSoup(requests.get(url).content, 'html.parser'))
    
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    print('----------------START----------------')
    while True:
        counts = 0
        for soup in soups:
            for tr in soup.find_all('tr', class_='')[3:]:
                tmp = tr.find('td', class_='title')
                title = tmp.a['title']
                page = tmp.a['href']
                tmp = tr.find_all('td', class_='')
                user = tmp[0].a.get_text()
                user_page = tmp[0].a['href']
                comments = tmp[1].get_text()
                c_time = tr.find('td', class_='time').get_text()

                if is_good(title) and (user not in exl):
                    counts = counts + 1
                    msg = """
                    title: 
                    %s

                    user: %s
                    user_page: %s
                    time: %s
                    comments: %s
                    detail: %s
                    """ % (title, user, user_page, c_time, comments, page)

                    itchat.send(msg, toUserName='filehelper')
                    print(msg)
                    ex.append({
                        'title': title,
                        'user': user,
                        'user_page': user_page,
                        'page': page,
                        'time': c_time,
                        'comments': comments
                    })
            if counts < 1:
                itchat.send('No new', toUserName='filehelper')
            
            with open(exf_name, 'w') as f:
                f.write(demjson.encode(ex))
        
        print('-------------sleeping 30s-------------')
        time.sleep(60*30)

        ex = demjson.decode_file(exf_name)
        

if __name__ == '__main__':
    main()
