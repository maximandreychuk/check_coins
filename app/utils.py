from bs4 import BeautifulSoup as bs
import requests


def convertStr(s: str):
    try:
        ret = round(float(s), 7)
    except ValueError:
        return None
    return ret


def getCapital(link):
    resp = requests.get(link).text
    soup = bs(resp, 'lxml')
    capital = soup.find(
        'div', class_='sc-65e7f566-0 DDohe flexStart alignBaseline').find_next('span').text
    try:
        ret = round(float(capital.split('$')[1]), 7)
    except ValueError:
        return None
    return ret
