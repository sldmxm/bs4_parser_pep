import re
import logging
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_DOC_URL, EXPECTED_STATUS
from outputs import control_output
from exceptions import ParserFindTagException
from utils import find_tag, get_soup, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)
    div_with_ul = find_tag(
        soup, 'div', attrs={'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        soup = get_soup(session, version_link)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    downloads = find_tag(soup, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        downloads, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = get_response(session, archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    def get_pep_status_in_doc(link):
        soup = get_soup(session, link)
        pep_overview = find_tag(
            soup,
            'dl',
            {'class': 'rfc2822 field-list simple'}
        )
        pep_status = find_tag(
            pep_overview,
            'Status',
            string=True,
        ).parent.find_next_sibling('dd')
        return pep_status.text

    soup = get_soup(session, PEP_DOC_URL)
    pep_by_index = find_tag(soup, 'section', {'id': 'numerical-index'})
    pep_table = find_tag(
        pep_by_index,
        'table',
        {'class': 'pep-zero-table docutils align-default'}
    )
    pep_table_body = find_tag(pep_table, 'tbody')

    statuses_count = {}
    mismatches = []
    total_pep = 0
    for row in tqdm(pep_table_body.find_all('tr')):
        pep_data = row.find_all('td')
        status_in_table = pep_data[0].text[1:]
        pep_link = urljoin(
                        PEP_DOC_URL,
                        find_tag(pep_data[2], 'a')['href']
                    )
        status_in_doc = get_pep_status_in_doc(pep_link)
        statuses_count[status_in_doc] = statuses_count.get(
            status_in_doc, 0) + 1
        total_pep += 1
        if status_in_doc not in EXPECTED_STATUS[status_in_table]:
            mismatches.append(
                (pep_link, EXPECTED_STATUS[status_in_table], status_in_doc)
            )
    for pep_link, status_in_table, status_in_doc in mismatches:
        logging.info('Несовпадающие статусы:'
                     f'{pep_link} '
                     f'Ожидаемые статусы: {status_in_table} '
                     f'Статус в карточке: {status_in_doc} '
                     )

    results = [('Status', 'Amount')]
    for status, count in statuses_count.items():
        results.append((status, count))
    results.append(('Total', total_pep))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode

    try:
        results = MODE_TO_FUNCTION[parser_mode](session)
    except ParserFindTagException as e:
        logging.error(e, exc_info=True)
        results = None

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
