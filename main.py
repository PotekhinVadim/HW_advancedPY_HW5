import requests
import json
from bs4 import BeautifulSoup
from fake_headers import Headers
from decorator_1 import logger

HOST = "https://spb.hh.ru"
FILTER = "/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_\
            field=description&enable_snippets=true&text=python"
LINK = f"{HOST}{FILTER}"


def get_headers():
    return Headers(browser="firefox", os="win").generate()


def get_text(url):
    return requests.get(url, headers=get_headers()).text


links_list = []
vacancies_list = []


def parse_vacancy_links():
    soup = BeautifulSoup(get_text(LINK), "lxml")
    vacancies = soup.find_all("a", class_="serp-item__title")
    for vacancy in vacancies:
        links = vacancy["href"]
        response_links = requests.get(links, headers=get_headers())
        links_parsed = BeautifulSoup(response_links.text, "lxml")
        vacancy_desc = links_parsed.find("div", {"data-qa": "vacancy-description"})
        if not vacancy_desc:
            continue
        if ("Django" or "Flask") in vacancy_desc.text:
            links_list.append(links)
    return links_list

@logger
def parse_vacation():
    for i in links_list:
        link = requests.get(i, headers=get_headers())
        vacancy_parsed = BeautifulSoup(link.text, "lxml")
        salary = vacancy_parsed.find(
            "span", class_="bloko-header-section-2 bloko-header-section-2_lite"
        )
        if not salary:
            continue
        city = vacancy_parsed.find("p", {"data-qa": "vacancy-view-location"})
        if not city:
            city = vacancy_parsed.find("span", {"data-qa": "vacancy-view-raw-address"})
            if not city:
                continue
        company_name = vacancy_parsed.find("a", {"data-qa": "vacancy-company-name"})
        if not company_name:
            continue
        vacancies_list.append(
            {
                "link": i,
                "salary": salary.text,
                "city": city.text,
                "company": company_name.text,
            }
        )
    return vacancies_list


if __name__ == "__main__":
    parse_vacancy_links()
    parse_vacation()
    with open("vacancies.json", "w", encoding="utf-8") as data:
        json.dump(vacancies_list, data, indent=2, ensure_ascii=False)
