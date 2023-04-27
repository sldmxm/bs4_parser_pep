import logging

from bs4 import BeautifulSoup

from exceptions import ParserFindTagException
from requests import RequestException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.error(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def get_soup(session, url):
    response = get_response(session, url)
    if response is None:
        return
    return BeautifulSoup(response.text, features='lxml')


def find_tag(soup, tag, attrs=None, string=None):
    if string:
        searched_tag = soup.find(string=tag, attrs=(attrs or {}))
    else:
        searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
