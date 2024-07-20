import csv
import requests
import os
import time
from .utils import convertStr
from . import keyboards as kb
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bs4 import BeautifulSoup as bs
from random import randint
# import get_coin

router = Router()


class Coin(StatesGroup):
    name = State()
    min_value = State()
    max_value = State()


@router.message(Command('start'))
async def start(message: Message):
    await message.answer(f'/choose_coin - пройти процесс добавления монеты для отслеживания \n'
                         '/get_coins - показать все доступные для отслеживания монеты\n'
                         '/start - нажмите для просмотра доступных команд\n'
                         '/reload_coins - обновить список топ 100 валют')


@router.message(Command('reload_coins'))
async def reload_coins(message: Message):
    await message.answer('Обновляется..')
    url = "https://coinmarketcap.com/"
    response = requests.get(url).text
    soup = bs(response, 'lxml')
    links = []
    find_class = soup.find('table').find_all('a')
    for cl in find_class:
        index = cl.get('href').find('/#markets')
        if index == -1:
            links.append(url+cl.get('href')[1:])
    await message.answer(f'Этап 1 из 3 пройден')

    titles = []
    for r in links:
        detail_resp = requests.get(r).text
        detail_soup = bs(detail_resp, 'lxml')
        try:
            title = detail_soup.find(
                'span', class_='sc-65e7f566-0 lsTl').text[:-1].split(' ')
        except AttributeError:
            pass
        titles.append(title[0])
    await message.answer(f'Этап 2 из 3 пройден')

    with open(f'./coins.csv', 'w', newline='') as out_csv:
        writer = csv.writer(out_csv, delimiter=",", lineterminator="\r")
        writer.writerow(['Name', 'Link'])
        cnt = 0
        for _ in range(len(titles)):
            writer.writerow([
                titles[cnt],
                links[cnt]
            ])
            cnt += 1
    await message.answer('Успешно обновлено')


@router.message(Command('get_coins'))
async def get_coins(message: Message):
    await message.answer('Cписок доступных валют')
    await message.reply_document(document=types.FSInputFile(path='./coins.csv'))


@router.message(Command('choose_coin'))
async def choose_coins(message: Message, state: FSMContext):
    await state.set_state(Coin.name)
    await message.answer('Введите валюту, посмотреть список доступных валют /get_coins')


@router.message(Coin.name)
async def add_name(message: Message, state: FSMContext):
    names = [row[0]
             for row in csv.reader(open('/Users/semras0tresh/Desktop/dev/test_task_avangard/coins.csv'))]
    if message.text in names:
        await state.update_data(name=message.text)
        await state.set_state(Coin.min_value)
        await message.answer('Введите минимальное значение')
    else:
        await message.reply('Введите монету из списка')


@router.message(Coin.min_value)
async def add_min_value(message: Message, state: FSMContext):
    await state.update_data(min_value=message.text)
    await state.set_state(Coin.max_value)
    await message.answer('Введите максимальное значение')


@router.message(Coin.max_value)
async def add_min_value(message: Message, state: FSMContext):
    await state.update_data(max_value=message.text)

    await message.answer(f'Нажмите чтобы отслеживать', reply_markup=kb.track)


@router.callback_query(F.data == 'track')
async def author(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    for row in csv.reader(open('/Users/semras0tresh/Desktop/dev/test_task_avangard/coins.csv')):
        if row[0] == data["name"]:
            resp = requests.get(row[1]).text
            soup = bs(resp, 'lxml')
            capital = soup.find(
                'span', class_='sc-65e7f566-0 clvjgF base-text').text
    capital = convertStr(capital.split('$')[1])
    data["min_value"] = convertStr(data["min_value"])
    data["max_value"] = convertStr(data["max_value"])
    while capital > data["min_value"] and capital < data["max_value"]:
        capital = soup.find(
            'span', class_='sc-65e7f566-0 clvjgF base-text').text
        capital = convertStr(capital.split('$')[1])
        data["min_value"] = convertStr(data["min_value"])
        data["max_value"] = convertStr(data["max_value"])
        await callback.message.answer(f'Монета отслеживается, текущая цена {capital}$')
        time.sleep(randint(1, 5))
    if capital <= data["min_value"]:
        await callback.message.answer(f'Монета достигла ваш минимум {data["min_value"]}, текущая цена {capital}$')
    elif capital >= data["max_value"]:
        await callback.message.answer(f'Монета достигла ваш максимум {data["max_value"]}, текущая цена {capital}$')
