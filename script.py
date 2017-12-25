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
        line = row[0]
        if line.startswith("https://"):
            add_link(line)
        else:
            add_user(line)
    log.info("Import finished")


def add_user(username):
    link = 'https://habrahabr.ru/users/' + username + "/";
    if (verify_link(link)):
        user = [username, link];
        userlist.append(user);
        log.info("User added")
    else:
        log.info("Bad username")

def add_link(link):
    if verify_link(link):
        linklist.append(link);
        log.info("Link added")
    else:
        log.info("Bad link")

def get_users():
    return userlist;

def get_links():
    return linklist;

def verify_link(link):
    ret = urlopen(link);
    if ret.code == 200:
        return True
    return False


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
    return links


def get_tree(post):
    def check():
        data = urlopen(post).read();
        return data.decode('utf-8', 'ignore');

    page = requests.get(post)
    return html.fromstring(page.content);


def fix_views(views):
    if views[-1] is 'k':
        if ',' in views:
            views = views.replace(',', '')
            views = float(views[:-1])
            return int(views * 100)
        else:
            views = float(views[:-1])
            return int(views * 1000)
    else:
        return int(views)


def compare(array1, array2):
    # Comparing last result with current, ignoring the date in current, flag for result
    for i in range(0, len(array1)):
        if array1[i] == array2[i]:
            continue
        else:
            return False
    return True


def get_stats(tree):
    result = [datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),
              int(tree.xpath(
                  '(//span[@class="voting-wjt__counter voting-wjt__counter_positive  js-score"]/text())[1]')[
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
    views = fix_views(views);

    # Appending values to array
    result.append(views)
    result.append(comments)
    return result


def get_previous_result(post):
    last_result = []
    reader = []
    try:
        reader = csv.reader(open(post[-7:-1] + ".csv"), delimiter=',', quotechar='|');
    except:
        log.info("No such file")
    reader = list(reader)
    last_result = []
    if reader:
        last_result = reader[-1]
        last_result = last_result[1:]
        # Convert str list to int list
        last_result = list(map(int, last_result))
    return last_result


def write_result(post, result):
    # Write new data
    out = csv.writer(open(post[-7:-1] + ".csv", "a"), delimiter=',', lineterminator='\n',
                     quoting=csv.QUOTE_NONE);
    out.writerow(result);


def main():
    import_data()
    posts = []
    for user in userlist:
        posts += get_all_user_posts(user);
    for link in linklist:
        posts.append(link);
    for post in posts:

        # Getting HTML tree for the post
        tree = get_tree(post);

        # Getting current stats for the post
        result = get_stats(tree);

        # Get previous result for the post
        previous_result = get_previous_result(post);

        # Check if there were previous result
        is_equal = False
        if len(previous_result) != 0:
            # Check if data changed
            is_equal = compare(previous_result, result[1:])
        if not is_equal:
            write_result(post, result);


# TODO Add try catch
# TODO Add Logger
# TODO optimize search of elements
if __name__ == "__main__":
    main()
