import requests
from bs4 import BeautifulSoup
from db import db
import json

BASE_URL = 'https://jut.su'

def fetch(link):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        code = BOLD + OKGREEN +  '[' + str(response.status_code) + ']' + ENDC
    else:
        code = BOLD + FAIL + '[' + str(response.status_code) + ']' + ENDC

    print('GET ' + code  + ': ' + link + ENDC)
    return response.text


def parse_episode_content(html_str):
    result = []
    s = BeautifulSoup(html_str, 'html.parser')
    for item in s.select('source'):
        src = item['src']
        label = item['label']
        res = item['res']
        v_type = item['type']
        result.append({
            'src': src,
            'label': label,
            'res': res,
            'type': v_type,
        })
    return result

def parse_duration(html_str):
    s = BeautifulSoup(html_str, 'html.parser')
    duration = s.find('meta', { 'itemprop': 'duration' })
    duration = duration["content"] if duration else None
    return duration


def parse_short_btn(item):
    url = item['href']
    if url[0] == '/':
        url = BASE_URL + url
    episode_page_str = fetch(url)
    content = parse_episode_content(episode_page_str)
    title = item.contents[1]
    subtitle = item['title']
    is_filler = len(item.contents) == 3

    return {
        'url': url,
        'title': title,
        'subtitle': subtitle,
        'isFiller': is_filler,
        'content': content,
    }


def parse_season_page(html_str):
    episodes = []
    s = BeautifulSoup(html_str, 'html.parser')
    for item in s.select('.watch_list_item .short-btn'):
        episodes.append(parse_short_btn(item))

    return episodes


def parse_seasons_list(html_str):
    seasons = []
    s = BeautifulSoup(html_str, 'html.parser')
    if len(s.select('.all_anime_content')) == 1:
        for item in s.select('.all_anime_global'):
            url = item.select('a')[0]['href']
            title = item.select('.all_anime_tooltip')[0]['title']
            episodes = parse_season_page(fetch(BASE_URL + url))
            seasons.append({
                'title': title,
                'episodes': episodes,
            })
    elif len(s.select('.watch_l .b-b-title')) > 0:
        for item in s.select('.watch_l .short-btn, .watch_l .b-b-title'):
            if item.name == 'h2':
                seasons.append({ 'title': item.get_text(), 'episodes': [] })
            else:
                seasons[-1]['episodes'].append(parse_short_btn(item))
    else:
        seasons.append({ 'title': 'DEFAULT', 'series': [] })
        for item in s.select('.watch_l .short-btn'):
            seasons[0]['episodes'].append(parse_short_btn(item))

    return seasons


def parse_anime_data(anime_slug):
    anime_page = fetch(BASE_URL + '/' + anime_slug)
    s = BeautifulSoup(anime_page, 'html.parser')
    title = s.find("meta", property="yandex_recommendations_title")
    title = title["content"] if title else None
    original_name = title
    if len(s.select('.under_video_additional b')) > 0:
        original_name = s.select_one('.under_video_additional b').get_text()
    seasons = parse_seasons_list(anime_page)
    return {
        'title': title,
        'originalName': original_name,
        'slug': anime_slug,
        'seasons': seasons,
    }


def scrap_anime(slug):
    query = { 'slug': slug }

    if len(list(db.animes.find(filter=query))) > 0:
        db.animes.update_one(query, { "$set": parse_anime_data(slug) })
    else:
        db.animes.insert_one(parse_anime_data(slug))

if __name__ == '__main__':
    # animes = ['tokushu', 'kimetsu-yaiba']
    scrap_anime('naruuto')
    # print(parse_seasons_list(open("test.html", "r", encoding='UTF-8').read()))

