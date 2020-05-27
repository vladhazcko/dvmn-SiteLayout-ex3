import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

BOOK_DIR = 'books'
IMG_DIR = 'images'


class ToluluBook():
    HOST = 'http://tululu.org'

    def __init__(self, book_id: int):
        self.id = book_id
        self.response = self.get_response()
        self.html_soup = self.get_html_soup()
        self.title = self.get_title()
        self.author = self.get_author()
        self.img_url = self.get_img_url()
        self.txt_file_url = self.get_txt_file_url()

    def get_response(self):
        url = f'http://tululu.org/b{self.id}/'
        response = requests.get(url)
        response.raise_for_status()
        return response

    def get_html_soup(self):
        is_exist_book_link = not bool(self.response.history)
        if not is_exist_book_link:
            return None

        soup = BeautifulSoup(self.response.text, features="lxml").find('div', id='content')
        r_expr = '/txt\.php\?id='
        a_tag_txt = soup.find('a', href=re.compile(r_expr))
        if a_tag_txt:
            return soup
        return None

    def is_valid(self):
        if self.html_soup:
            return True
        return False

    def get_title(self):
        if not self.is_valid():
            return None
        title = self.html_soup.find('h1').text.split('::')[0].strip()
        return title

    def get_author(self):
        if not self.is_valid():
            return None
        author = self.html_soup.find('h1').find('a').text
        return author

    def get_img_url(self):
        if not self.is_valid():
            return None
        img_tag = self.html_soup.find('table', class_='d_book').find('img')
        img_url = urljoin(self.HOST, img_tag['src'])
        return img_url

    def get_txt_file_url(self):
        url = f'{self.HOST}/txt.php?id={self.id}'
        return url

    def get_file_name(self):
        return f'{self.id}. {self.title}'


def download_file(url, filename, file_extension, folder):
    path = os.path.join(folder, sanitize_filename(filename)) + file_extension
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as txt_file:
        txt_file.write(response.content)
    return path


def download_img(url, folder=IMG_DIR):
    path = url.split("/")[-1]
    filename, file_extension = os.path.splitext(path)
    download_file(
        url=url,
        filename=filename,
        file_extension=file_extension,
        folder=folder
    )


def download_txt(url, filename, folder=BOOK_DIR):
    file_extension = '.txt'
    download_file(
        url=url,
        filename=filename,
        file_extension=file_extension,
        folder=folder
    )


def main():
    Path(BOOK_DIR).mkdir(parents=True, exist_ok=True)
    Path(IMG_DIR).mkdir(parents=True, exist_ok=True)

    books_count = 10
    for book_id in range(1, 1 + books_count):
        book = ToluluBook(book_id)
        if not book.is_valid():
            continue

        print(book.title)
        print(book.img_url)
        txt_name = book.get_file_name()

        download_txt(url=book.txt_file_url, filename=txt_name)
        download_img(url=book.img_url)


if __name__ == '__main__':
    main()
