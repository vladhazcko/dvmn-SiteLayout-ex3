import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

import os, re


class ToluluBook():
    HOST = 'http://tululu.org'

    def __init__(self, book_id: int):
        self.id = book_id
        self.response = self.get_response()
        self.html_soup = self.get_html_soup()
        self.title = self.get_title()
        self.author = self.get_author()
        self.img_src = self.get_img_src()
        self.download_url = self.get_download_url()

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

    def get_img_src(self):
        if not self.is_valid():
            return None
        img_tag = self.html_soup.find('table', class_='d_book').find('img')
        img_src = img_tag['src'] if 'http' in img_tag else self.HOST + img_tag['src']
        return img_src

    def get_download_url(self):
        url = f'{self.HOST}/txt.php?id={self.id}'
        return url

    def get_filename(self):
        return f'{self.id}. {self.title}'


def download_txt(url, filename, folder='books/'):
    path = os.path.join(folder, sanitize_filename(filename)) + '.txt'
    response = requests.get(url)
    response.raise_for_status()

    with open(path, 'w') as txt_file:
        txt_file.write(response.text)
    return path


def main():
    books_directory = 'books'
    Path(books_directory).mkdir(parents=True, exist_ok=True)

    books_count = 10
    for book_id in range(1, 1 + books_count):
        book = ToluluBook(book_id)
        if not book.is_valid():
            continue

        print(book.title)
        print(book.img_src)
        print(book.author)
        file_name = book.get_filename()
        print(download_txt(book.download_url, file_name))


if __name__ == '__main__':
    main()
