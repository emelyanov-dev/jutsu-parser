import requests
from db import db


def fetch_video(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, headers=headers)
    return response.content


if __name__ == '__main__':
    anime = db.animes.find_one(filter={ 'slug': 'naruuto' })
    for index, season in enumerate(anime['seasons']):
        for episodeIndex, episode in enumerate(season['episodes']):
            expisode_url = episode['content'][0]['src']
            video = fetch_video(expisode_url)
            print(expisode_url)
            open('media/naruto-' + str(index) + '-' + str(episodeIndex) + '.mp4' , "wb").write(video)

