from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import (
    ParserFindTagException,
    ParserNoneResponseException,
    ParserRequestException,
)


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        raise ParserRequestException(
            f'Ошибка при загрузке страницы {url}'
        ) from None


def get_soup(session, url):
    response = get_response(session, url)
    if response is None:
        error_msg = f'Пустой ответ сервера {url}'
        raise ParserNoneResponseException(error_msg)
    return BeautifulSoup(response.text, features='lxml')


def find_tag(soup, tag, attrs=None, string=None):
    if string:
        searched_tag = soup.find(string=tag, attrs=(attrs or {}))
    else:
        searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        raise ParserFindTagException(error_msg)
    return searched_tag
