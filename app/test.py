from bs4 import BeautifulSoup as bs
import requests


def getCapital(link):
    resp = requests.get(link).text
    soup = bs(resp, 'lxml')
    capital = soup.find(
        'div', class_='sc-65e7f566-0 DDohe flexStart alignBaseline').find_next('span').text
    lst = ['.' if x == ',' else x for x in capital]
    capital = ''.join(lst).split('$')[1]

    dot_count = 0
    for index, char in enumerate(capital):
        if char == '.':
            dot_count += 1
        if dot_count == 2:
            return capital[:index]
    try:
        ret = round(float(capital), 10)
    except ValueError:
        return 0
    return ret


print(getCapital('https://coinmarketcap.com/currencies/bitcoin/'))
print(getCapital('https://coinmarketcap.com/currencies/dogecoin/'))
print(getCapital('https://coinmarketcap.com/currencies/ethereum/'))
