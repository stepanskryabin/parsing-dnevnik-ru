from bs4 import BeautifulSoup
from selenium import webdriver
import configparser

# ************** Read "config.ini" ********************
config = configparser.ConfigParser()
config.read('config.ini')
USER = config['USER']
PARAMETERS = config['PARAMETERS']
# ************** END **********************************

YEAR = "2020"

MOTHN = '9'

DAY = "1"

PERIOD = {
    "1-trimester": "1709395996654255174",
    "2-trimester": "1709395996654255175",
    "3-trimester": "1709395996654255174"}

URL = 'https://login.dnevnik.ru/login/esia/kir'


def get_info(html):
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', id='editor')
    tbody = table.find('tbody')
    tr = tbody.find_all('tr')
    table_head = []
    text = []

    # Отбираем заголовки таблицы с названием дня
    for item in tr:
        th = item.find_all('th')
        for item in th:
            head = item.find('a')
            if head is None:
                continue
            else:
                table_head.append(head.text)

    # Отбираем ячейки таблицы с именем урока
    for item in tr:
        td = item.find_all('td')
        for item in td:
            div = item.find_all('div')
            for item in div:
                a = item.find('a')
                if a is None:
                    a = "Отсутствует"
                else:
                    a = a.text
                text.append(a)
    print(table_head)
    print(text)
    return  #data


def get_classes(html) -> list:
    soup = BeautifulSoup(html, 'lxml')
    ul = soup.find('ul', class_='classes')
    li = ul.find_all('li')
    data = []
    for item in li:
        first_ul = item.find_all('ul')
        for item in first_ul:
            url = item.find('a').get('href')
            class_name = item.find('a').text
            element = {"class_name": class_name, "url": url}
            data.append(element)
    return data


def main(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=options)
    browser.implicitly_wait(5)
    browser.get(url)
    browser.find_element_by_name('login').clear()
    browser.find_element_by_name('login').send_keys(USER.get('login'))
    browser.find_element_by_name('password').clear()
    browser.find_element_by_name('password').send_keys(USER.get('password'))
    browser.find_element_by_xpath("//input[@type='submit'][@data-test-id='login-button']").click()
    browser.implicitly_wait(5)
    browser.get(f'https://schools.dnevnik.ru/schedules/?school={PARAMETERS.get("school")}&tab=groups&year={YEAR}')
    link_to_all_classes = get_classes(browser.page_source)
    link_to_1a_class = link_to_all_classes[0]['url']
    schedules = f'{link_to_1a_class}&period={PERIOD}&year={YEAR}&month={MOTHN}&day={DAY}'
    browser.get(schedules)
    result = browser.page_source
    return print("DATA: ", get_info(result))


if __name__ == "__main__":
    main(URL)
