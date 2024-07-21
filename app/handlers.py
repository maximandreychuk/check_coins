import csv
import requests
import sqlite3
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


router = Router()
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()


class Coin(StatesGroup):
    name = State()
    min_value = State()
    max_value = State()


@router.message(Command('start'))
async def start(message: Message):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS coins (
                id INTEGER PRIMARY KEY,
                name REAL,
                min REAL,
                max REAL,
                cap REAL
    );
        """)
    await message.answer(f'/choose_coin - пройти процесс добавления монеты для отслеживания \n'
                         '/get_coins - показать все доступные для отслеживания монеты\n'
                         '/start - нажмите для просмотра доступных команд\n'
                         '/reload_coins - обновить список топ 100 валют\n')
    #  '/clear_coins - очистить отслеживаемые монеты\n'
    #  '/my_coins - все мои отслеживаемые монеты')


@router.message(Command('my_coins'))
async def clear_db(message: Message):
    cursor.execute(
        f'SELECT * FROM coins;')
    res = cursor.fetchall()
    print(res)
    await message.answer(f"(Монета, Минимум, Максимум, Цена)\n{res[0][1:]}")


@router.message(Command('clear_coins'))
async def clear_db(message: Message):
    cursor.execute(
        f'DELETE FROM coins;')
    conn.commit()
    await message.answer('Больше нет отслеживаемых монет\nНачать заново /choose_coins')


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
    await message.answer('Введите название монеты, посмотреть список доступных валют /get_coins')


@router.message(Coin.name)
async def add_name(message: Message, state: FSMContext):
    coins = {row[0]: row[1]
             for row in csv.reader(open('/Users/semras0tresh/Desktop/dev/test_task_avangard/coins.csv'))}
    if message.text in coins.keys():
        resp = requests.get(coins[message.text]).text
        soup = bs(resp, 'lxml')
        current_cap = soup.find(
            'div', class_='sc-65e7f566-0 DDohe flexStart alignBaseline').find_next('span').text
        current_cap = convertStr(current_cap.split('$')[1])
        await message.answer(f'Ссылка {coins[message.text]}\nТекущая цена {current_cap}$')
        await state.update_data(name=message.text)
        data = await state.get_data()
        cursor.execute(
            f'INSERT INTO coins (name) SELECT("{data['name']}") WHERE NOT EXISTS (SELECT name FROM coins WHERE name = "{data['name']}") LIMIT 1;')
        conn.commit()
        cursor.execute(f'UPDATE coins SET cap = "{current_cap}" WHERE name = "{data['name']}"')
        conn.commit()
        await state.set_state(Coin.min_value)
        await message.answer('Введите минимальное значение')
    else:
        await message.reply('Введите монету из списка')


@router.message(Coin.min_value)
async def add_min_value(message: Message, state: FSMContext):
    await state.update_data(min_value=message.text)
    data = await state.get_data()
    cursor.execute(
        f'UPDATE coins SET min = "{data['min_value']}" WHERE name = "{data['name']}"')
    conn.commit()
    await state.set_state(Coin.max_value)
    await message.answer('Введите максимальное значение')


@router.message(Coin.max_value)
async def add_min_value(message: Message, state: FSMContext):
    await state.update_data(max_value=message.text)
    data = await state.get_data()
    cursor.execute(
        f'UPDATE coins SET max = "{data['max_value']}" WHERE name = "{data['name']}"')
    conn.commit()
    await message.answer(f'Нажмите, чтобы отслеживать', reply_markup=kb.track)


@router.callback_query(F.data == 'track')
async def author(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['min_value'] > data['max_value']:
        await callback.message.answer('Максимальное значение не может быть меньше минимального, пройти заново /choose_coin')
    else:
        for row in csv.reader(open('/Users/semras0tresh/Desktop/dev/test_task_avangard/coins.csv')):
            if row[0] == data["name"]:
                resp = requests.get(row[1]).text
                soup = bs(resp, 'lxml')
                capital = soup.find(
                    'div', class_='sc-65e7f566-0 DDohe flexStart alignBaseline').find_next('span').text
        capital = convertStr(capital.split('$')[1])
        data["min_value"] = convertStr(data["min_value"])
        data["max_value"] = convertStr(data["max_value"])
        await callback.message.answer(f'Монета отслеживается, текущая цена {capital}$,\nВыбрать другую монету /choose_coin')
        while capital > data["min_value"] and capital < data["max_value"]:
            capital = soup.find(
                'span', class_='sc-65e7f566-0 clvjgF base-text').text
            capital = convertStr(capital.split('$')[1])
            data["min_value"] = convertStr(data["min_value"])
            data["max_value"] = convertStr(data["max_value"])
            time.sleep(randint(1, 5))
        if capital <= data["min_value"]:
            await callback.message.answer(f'Монета достигла ваш минимум {data["min_value"]}, текущая цена {capital}$')
        elif capital >= data["max_value"]:
            await callback.message.answer(f'Монета достигла ваш максимум {data["max_value"]}, текущая цена {capital}$')
