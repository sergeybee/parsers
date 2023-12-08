import time
import csv
from dataclasses import dataclass

from requests import Response, Session

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup


@dataclass
class Housebook:
    title: str
    price: str
    rental: str
    link: str
    constructor: str
    square: str
    contribution: str
    image: str


def create_csv_file():
    with open("data.csv", mode="w", newline="", encoding="utf-8") as fo:
        writer = csv.writer(fo)
        writer.writerow([
            "Название",
            "Срок сдачи",
            "Цена",
            "Ссылка",
            "Застройщик",
            "Площадь",
            "Первоначальный взнос",
            "Фото"
        ])


def write_to_csv_file(housebooks: list[Housebook]):
    with open("data.csv", mode="a", encoding="utf-8") as fo:
        writer = csv.writer(fo)
        for house in housebooks:
            writer.writerow([
                house.title,
                house.rental,
                house.price,
                house.link,
                house.constructor,
                house.square,
                house.contribution,
                house.image
            ])


def save_html_source_to_file(res: Response) -> None:
    with open("src_html", "w") as fo:
        fo.write(res.text)


def read_html_file(html_file) -> str:
    with open(html_file, "r") as fo:
        src_html = fo.read()
        return src_html


def get_housebook_data():
    print(f'[INFO] Старт парсера...')
    time.sleep(2)
    print(f'[INFO] Настраивается парсер...')
    time.sleep(2)

    option = Options()
    option.headless = True
    option.add_argument("--window-size=1920,1200")
    # option.add_argument("--start-maximized")
    option.add_argument("--disable-infobars")
    # option.add_argument('--headless=new')
    custom_user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.3.706 Yowser/2.5 Safari/537.36'
    option.add_argument(f'user-agent={custom_user_agent}')

    print(f'[INFO] Запускается браузер...')
    time.sleep(1)
    browser = webdriver.Firefox(options=option)

    browser.get('https://housebook.ae/ru/zhilye-kompleksy')

    def scroll_page_to_element():
        web_items = browser.find_elements(By.CSS_SELECTOR, "div[class='mb-6 b-box project-card -horizontal")
        for block in web_items:
            if len(web_items) != 1:
                browser.execute_script("arguments[0].scrollIntoView();", block)
                time.sleep(1)
            else:
                pass

    housebooks = []

    print(f'[INFO] Идет сбор данных, ожидайте...')

    for page_number in range(1, 12 + 1):

        if page_number != 1:
            browser.find_element(By.CSS_SELECTOR,
                                 f"ul[class='v-pagination theme--light'] li button[aria-label='Goto Page {page_number}']").click()
        else:
            browser.find_element(By.CSS_SELECTOR,
                                 f"ul[class='v-pagination theme--light'] li button[aria-label='Current Page, Page {page_number}']").click()

        scroll_page_to_element()

        src_html = browser.page_source

        soup = BeautifulSoup(src_html, "lxml")
        blocks = soup.select("div[class='mb-6 b-box project-card -horizontal']")

        print(f'[INFO] Парсим страницу {page_number}...')

        for i in blocks:
            title = i.find("div", class_="b-box mb-2 -flex").find("h6").getText(strip=True)
            price = i.find("div", class_="b-box mb-4").find("h5").getText(strip=True)
            rental = i.find("div", class_="typography mb-2 -t145006 -inherit -left").text.strip().split("г")[0].replace(
                "Сдача", "").strip()
            link = f"https://housebook.ae/ru/zhilye-kompleksy/" + \
                   i.find("div", class_="b-box -flex").find("a").get("href").split("/ru/zhilye-kompleksy/")[1]

            square_block = i.select("div[class='b-box -flex-column']")

            constructor = (
                square_block[0].find_all("span", class_="typography right-prop -t144005 -inherit -left")[0]).text
            square = (
                square_block[0].find_all("span", class_="typography right-prop -t144005 -inherit -left")[
                    1]).text.strip()
            contribution = (
                square_block[0].find_all("span", class_="typography right-prop -t144005 -inherit -left")[
                    2]).text.strip()
            img = i.select("div[class='v-image__image v-image__image--cover']")[0].get("style")
            image = img.split('("')[1].split('")')[0].strip()

            housebooks.append(Housebook(
                title=title,
                rental=rental,
                price=price,
                link=link,
                constructor=constructor,
                square=square,
                contribution=contribution,
                image=image
            ))

    create_csv_file()
    time.sleep(2)
    write_to_csv_file(housebooks)

    browser.quit()


if __name__ == "__main__":
    try:
        get_housebook_data()

    except (KeyboardInterrupt, SystemExit) as err:
        print(f"Program stopped\n"
              f"{err}")