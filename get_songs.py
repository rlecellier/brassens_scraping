from bs4 import BeautifulSoup
import requests
import re

SAVE_DIR = '/home/rlecellier/tmp/Brassens'

SITE_HOST = "https://paroles2chansons.lemonde.fr"
SONG_INDEX_URL = f'{SITE_HOST}/paroles-georges-brassens'

song_index_response = requests.get(SONG_INDEX_URL)
song_index_soup = BeautifulSoup(song_index_response.text, 'html.parser')

pagination_url_pattern = r'https://paroles2chansons.lemonde.fr/paroles-georges-brassens-p[0-9]{1,2}'
page_links = song_index_soup.find_all(href=lambda href: href and re.search(pagination_url_pattern, href))

song_url_pattern = '/paroles-georges-brassens/paroles-'
song_links = song_index_soup.find_all(href=lambda href: href and re.search(song_url_pattern, href))

page_urls = set([page_link['href'] for page_link in page_links])
for url in page_urls:
    page_index_response = requests.get(url)
    page_index_soup = BeautifulSoup(page_index_response.text, 'html.parser')
    song_links = song_links + page_index_soup.find_all(href=lambda href: href and re.search(song_url_pattern, href))

# hackish, better not to parse twice the page 1.
song_urls = set([f'{SITE_HOST}{song_link["href"]}' for song_link in song_links])

for song_url in song_urls:
    print(f'--- Get {song_url}')
    song_response = requests.get(song_url)
    song_soup = BeautifulSoup(song_response.text, 'html.parser')

    song_container = song_soup.find(
        attrs={'class': lambda elmClasses: elmClasses and re.search('songCredits', elmClasses)}
    ).find_next_sibling('div')

    title = song_container.h1.text.replace('Lyrics & Traduction', '').strip()

    file_name = re.sub(f"[ ,'\-:]", '_', title)
    file_name = re.sub(f"_+", '_', file_name)

    print('--- --- Parse song', file_name)

    fp = open(f'{SAVE_DIR}/{file_name}.txt', 'w+', encoding="utf-8")
    fp.write(title)
    fp.write('\n')
    fp.write('\n')

    container_divs = song_container.find_all('div')
    for div in container_divs:
        song_part = div.text.strip()
        if song_part and not re.search('Paroles2Chansons', song_part):
            fp.write(song_part)
    fp.write('\n')
    fp.close()

