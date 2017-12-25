import lxml.html
import os
from lxml import html
from urllib.request import urlopen
from math import ceil
import csv
import requests
import datetime
import logging

# TODO Adapt arguement
# TODO User storage and data storage
# TODO User read

userlist = []
linklist = []

log = logging.getLogger("my-logger")
log.info("New session")




def import_data():
    file = open("data.csv", 'r');
    reader = csv.reader(file)
    for row in reader:
        if row.startswith("https://"):
            add_link(row)
        else:
            add_user(row)
    log.info("Import finished")

def add_user(username):
    link = 'https://habrahabr.ru/users/' + username + "/";
    user = [username, link];
    userlist.append(user);
    log.info("User added")

def add_link(link):
    linklist.append(link);
    log.info("Link added")

def print_links():
    for i in linklist:
        print(i);


def print_users():
    for i in userlist:
        print(i);


def print_all():
    print_links();
    print_users();


def get_all_user_posts(user):
    post_link = user[1] + "posts/page";
    data = urlopen(post_link).read();
    res = data.decode('utf-8', 'ignore');
    root = lxml.html.document_fromstring(res)
    number_of_posts = int(root.xpath("//*[contains(@class, \
                                     'tabs-menu__item-counter tabs-menu__item-counter_total')]")[
                              0].text_content().strip())
    number_of_pages = ceil(number_of_posts / 10)
    print(number_of_pages);
    links = [];
    for i in range(number_of_pages - 1):
        post_link += str(i);
        data = urlopen(post_link).read();
        res = data.decode('utf-8', 'ignore');
        root = lxml.html.document_fromstring(res)
        links += root.xpath("//*/article/h2/a/@href")

    # Create dir for the CSVs
    if not os.path.exists("csv"):
        os.makedirs("csv")

    # Create file for every post
    for i in links:
        # open(i[26:31].csv, 'w')
        print(i)
    return links


# TODO optimize search of elements

add_user("fruct")
add_user("habr")
print_users()
posts = get_all_user_posts(userlist[0])

# getting post link
for post in posts:
    def check():
        data = urlopen(post).read();
        return data.decode('utf-8', 'ignore');


    page = requests.get(post)
    tree = html.fromstring(page.content);

    # getting date, rating and bookmarks
    result = [int(tree.xpath('(//span[@class="voting-wjt__counter voting-wjt__counter_positive  js-score"]/text())[1]')[
                      0]),
              int(tree.xpath('//span[@class="bookmark__counter js-favs_count"]/text()')[0])]

    # Comments may not exist, therefore we check
    comments = tree.xpath('//span[@class="post-stats__comments-count"]/text()')
    if len(comments) is 0:
        comments = 0
    else:
        comments = int(comments[0])

    # getting views, removing 1k and making it a number
    views = tree.xpath('//span[@class="post-stats__views-count"]/text()')[0]
    if views[-1] is 'k':
        if ',' in views:
            views = views.replace(',', '')
            views = float(views[:-1])
            views = int(views * 100)
        else:
            views = float(views[:-1])
            views = int(views * 1000)
    else:
        views = int(views)

    # Appending values to array
    result.append(views)
    result.append(comments)

    #datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    '''
    Working with file, reading and writing
    '''

    # TODO Add try catch
    # TODO Add Logger
    # Read the file in mode for reading and appending, naming is id of the post from link
    try:
        file = open(post[26:32] + ".csv", "a+");
    except:
        log.info("Error while opening file")
    is_equal = False;
    file_lines = file.readlines();
    if len(file_lines) != 0:
        # get last line from csv to compare it with current
        last_line = file_lines[len(file_lines) - 1]

        # remove date and time from comparison
        last_line = last_line.split(',')[1:];

        # Comparing last result with current, ignoring the date in current, flag for result
        for i in last_line:
            if i == result[i + 1]:
                is_equal = True
            else:
                continue
    if is_equal is False:
        out = csv.writer(file, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_ALL);
        out.writerow(result);
        file.close();
    print(result)
    print('---')
    doc = lxml.html.document_fromstring(check())
    '''
    element = doc.xpath("//span[contains(@class, 'post-stats__views-count') \
                       or contains(@class,'bookmark__counter js-favs_count') \
                       or (contains(@class, 'voting-wjt__counter voting-wjt__counter_positive  js-score'))[1] \
                       or contains(@class, 'post-stats__comments-count')]")
    
    print(len(element))
    for i in range(len(element)):
        print(format(element[i].text_content().strip()))
    print("--")
    '''
