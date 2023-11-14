import requests
import re
from bs4 import BeautifulSoup as bs

# https://dev-event.vercel.app/events

def get_urls(url):
    response = requests.get(url)
    html = response.text
    soup = bs(html, 'html.parser')
    return soup

def get_hashtag(soup):
    hashtags_all = soup.find_all('div', class_='Item_tags___ujeV')
    hashtags  = []
    for hash in hashtags_all:
        txt = hash.text.split("# ")
        hashtags.append(txt[1:])
    return hashtags

def get_title(soup):
    title_all = soup.find_all('span', class_='Item_item__content__title___fPQa')
    titles = []
    for title in title_all:
        titles.append(title.text)
    return titles

def get_host(soup):
    hosts_all = soup.find_all('div', class_='Item_host__zNXMy')
    hosts = []
    for host in hosts_all:
        hosts.append(host.text)
    return hosts

def get_date(soup):
    dates_all = soup.find_all('div', class_='Item_date__kVMJZ')
    dates = []
    for date in dates_all:
        txt = re.sub(r"\s", "", date.text)
        txt = re.sub(r"\(.\)", "", txt)
        dates.append(txt.split("~"))
    return dates

def get_image(soup):
    images_all = soup.find_all('img', alt="/default/event_img.png")
    images = []
    for image in images_all:
        text = 'https://dev-event.vercel.app'
        text += image.get('src')
        images.append(text)
    return images

def get_link(soup):
    link_all = soup.find_all('div', class_='Item_item__86e_I')
    links = []
    for link in link_all:
        txt = link.a.attrs["href"]
        links.append(txt)
    return links

def main():
    url = 'https://dev-event.vercel.app/events'
    soup = get_urls(url)
    hastags = get_hashtag(soup) # 해시태그
    # print(hastags)
    titles = get_title(soup) # 제목
    # print(titles)
    hosts = get_host(soup) # 주최자
    # print(hosts)
    dates = get_date(soup) # 일시[시작일, 종료일]
    # print(dates)
    images = get_image(soup) # 이미지
    # print(images)
    links = get_link(soup) # 주최 링크
    # print(links)

if __name__ == '__main__':
    main()

