import bs4 as bs
import numpy as np
import os as os
import pandas as pd
import pathlib as pl
import re
import requests as rq
import slugify as sg
import string as st
import unicodedata as uc
import urllib as ul


global USER
USER = os.getcwd().split('/')[2]


def get_artists():
    url_start = 'https://www.wikiart.org/en/Alphabet/'
    url_end = '/text-list'
    url_class = 'masonry-text-view-all'
    headers = {'User-Agent': 'Mozilla/5.0'}

    artists = pd.DataFrame(columns=['artist', 'url', 'life', 'artworks'])

    for letter in st.ascii_lowercase:

        r = rq.get(url_start + letter + url_end, headers=headers)
        soup = bs.BeautifulSoup(r.text, 'html.parser')

        page = soup.find("div", class_=url_class)

        for l in page.find_all('li'):
            try:
                name = l.a.text
            except:
                name = None
            try:
                link = l.a['href']
            except:
                link = None
            try:
                life = l.span.text
            except:
                life = None
            try:
                artworks = l.find_all('span')[1].text
            except:
                artworks = None

            artist = pd.DataFrame([[name, link, life, artworks]],
                                  columns=['artist', 'url', 'life', 'artworks'])
            artists = artists.append(artist)

    artists = artists.reset_index(drop=True)

    for index, row in artists[artists['artworks'].isna()].iterrows():
        artists.loc[index, 'artworks'] = artists.loc[index, 'life']
        artists.loc[index, 'life'] = None

    return artists


def get_artworks():
    url_start = 'https://www.wikiart.org'
    url_end = '/all-works/text-list'
    url_class = 'painting-list-text-row'
    headers = {'User-Agent': 'Mozilla/5.0'}

    artists = get_artists()

    artworks = pd.DataFrame(columns=['artist', 'name', 'url', 'year'])
    for index, row in artists.iterrows():
        print(index, 'out of', artists.shape[0])

        r = rq.get(url_start + row['url'] + url_end, headers=headers)
        soup = bs.BeautifulSoup(r.text, 'html.parser')

        page = soup.find_all("li", class_=url_class)

        for tag in page:
            try:
                artist = row['artist']
            except:
                artist = None
            try:
                link = tag.a['href']
            except:
                link = None
            try:
                name = tag.a.text
            except:
                name = None
            try:
                year = tag.span
            except:
                year = None

            artwork = pd.DataFrame([[artist, name, link, year]],
                                   columns=['artist', 'name', 'url', 'year'])
            artworks = artworks.append(artwork)

    artworks = artworks.reset_index(drop=True)

    url_start = 'https://www.wikiart.org'
    url_end = '/all-works/text-list'

    url_class = 'ms-zoom-cursor'

    for index, row in artworks.iterrows():
        if index % 100 == 0:
            print(index, 'out of', artworks.shape[0])

        if not (row['url'] is None or str(row['url']) == 'nan'):
            try:
                r = rq.get(url_start + str(row['url']), headers=headers)
                soup = bs.BeautifulSoup(r.text, 'html.parser')
                page = soup.find("img", class_=url_class)
                artworks.loc[index, 'image'] = page['src']
            except:
                continue

    artworks = artworks.reset_index(drop=True)
    return artworks


def make_directories(artists):
    for artist in artists:
        pl.Path('/pool001/' + USER + '/Connoisseur/Artworks/'+str(artist)).mkdir(parents=True, exist_ok=True)


def load_artists():
    return pd.read_csv('/pool001/' + USER + '/Connoisseur/Data/artists.csv')


def load_artworks():
    return pd.read_csv('/pool001/' + USER + '/Connoisseur/Data/artworks.csv')


def get_images():
    artworks = load_artworks()
    log = open('/pool001/' + USER + '/Connoisseur/Logs/images.log', 'w')
    artworks['idx'] = list(range(artworks.shape[0]))
    for i, r in artworks.iterrows():
        if (i%100==0) and i!=0:
            print('Completed', i, 'over', artworks.shape[0], 'images.')
        if r['image'] != np.nan:
            if os.path.isfile('/pool001/' + USER + '/Connoisseur/Artworks/' +str(r['artist']) + '/' +
                              sg.slugify(str(r['idx'])+'-'+uc.normalize('NFKD', r['name']).encode('ASCII', 'ignore').decode('ascii'))[:200] +
                              '.' + str(str(r['image']).split('.')[-1])) == False:
                try:
                    ul.request.urlretrieve(ul.request.quote(r['image'], safe=':/'),
                              '/pool001/' + USER + '/Connoisseur/Artworks/' + str(r['artist']) + '/' +
                              sg.slugify(str(r['idx'])+'-'+uc.normalize('NFKD', r['name']).encode('ASCII', 'ignore').decode('ascii'))[:200] +
                              '.' + str(str(r['image']).split('.')[-1]))
                except Exception as e:
                    log.write("Failed to download {0}: {1}\n".format(str(r['name']), str(e)))


def list_files(directory):
    elements = os.listdir(directory)
    all_files = list()
    for idx, entry in enumerate(elements):
        path = os.path.join(directory, entry)
        if os.path.isdir(path):
            all_files = all_files + list_files(path)
        else:
            all_files.append(path)
        if idx % 1000 == 0:
            print('{} images found'.format(idx))
    return all_files
