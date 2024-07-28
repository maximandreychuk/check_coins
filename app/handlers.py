from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from bs4 import BeautifulSoup as bs
from random import randint
from .database_settings import Сurrency, db
from .utils import getCapital, convertStr
from . import keyboards as kb


import csv
import requests
import os
import time
import asyncio

router = Router()


class Coin(StatesGroup):
    name = State()
    min_value = State()
    max_value = State()


class BoolFlag(StatesGroup):
    stop_track = State()


@router.message(Command('start'))
async def start(message: Message):
    db.create_tables([Сurrency,])
    await message.answer('Для начала нажмите /reload_coins')


@router.message(Command('help'))
async def reload_coins(message: Message):
    await message.answer('/choose_coin - пройти процесс добавления монеты для отслеживания\n'
                         '/get_coins - показать все доступные для отслеживания монеты\n'
                         '/clear_coins - очистить отслеживаемые монеты\n'
                         '/my_coins - все мои отслеживаемые монеты\n\n'
                         '/help - нажмите для просмотра доступных команд\n'
                         '/reload_coins - обновить список валют\n')


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

    with open(f'./oldcoins.csv', 'w', newline='') as out_csv:
        writer = csv.writer(out_csv, delimiter=",", lineterminator="\r")
        writer.writerow(['Name', 'Link'])
        cnt = 0
        for _ in range(len(titles)):
            writer.writerow([
                titles[cnt],
                links[cnt]
            ])
            cnt += 1

    reader = csv.reader(open('./oldcoins.csv', 'r'), delimiter=',')
    writer = csv.writer(open('./coins.csv', 'w'), delimiter=',')
    entries = set()
    for row in reader:
        if row[0] not in entries:
            writer.writerow(row)
            entries.add(row[0])
    os.remove('./oldcoins.csv')
    await message.answer('Отлично, теперь вы можете добавить монету '
                         'для отслеживания /choose_coin\n'
                         'Просмотреть монеты /get_coins\n'
                         'Все доступные команды /help')


@router.message(Command('my_coins'))
async def clear_db(message: Message):
    coins_list = []
    my_coins = Сurrency.select().where(Сurrency.user == message.from_user.username)
    for coin in my_coins:
        coins_list.append([f'Монета - {coin.name}', f'Минимум - {coin.min}',
                          f'Максимум - {coin.max}',])
    counter = 0
    while counter < len(coins_list):
        await message.answer(f'{coins_list[counter]}')
        counter += 1
    if len(coins_list) == 0:
        await message.answer('Нет отслеживаемых монет\nДобавить /choose_coin')


@router.message(Command('clear_coins'))
async def clear_db(message: Message):
    Сurrency.delete().where(Сurrency.user == message.from_user.username).execute()
    await message.answer('Больше нет отслеживаемых монет\nНачать заново /choose_coin')


@router.message(Command('get_coins'))
async def get_coins(message: Message):
    await message.answer('Cписок доступных валют')
    await message.reply_document(document=types.FSInputFile(path='./coins.csv'))


@router.message(Command('choose_coin'))
async def choose_coins(message: Message, state: FSMContext):
    await state.set_state(Coin.name)
    await message.answer('Введите название монеты, посмотреть '
                         'список доступных валют /get_coins')


@router.message(Coin.name)
async def add_name(message: Message, state: FSMContext):
    full_path = os.path.abspath('./coins.csv')
    coins = {row[0]: row[1]
             for row in csv.reader(open(full_path))}
    if message.text in coins.keys():
        current_cap = getCapital(coins[message.text])
        await message.answer(f'Ссылка {coins[message.text]}\nТекущая цена {current_cap}$')
        await state.update_data(name=message.text)
        await state.set_state(Coin.min_value)
        await message.answer('Введите минимальное значение в формате "0.9"')
    else:
        await message.reply('Введите монету из списка')


@router.message(Coin.min_value)
async def add_min_value(message: Message, state: FSMContext):
    if convertStr(message.text) == None:
        await message.answer('Не тот формат, давайте заново /choose_coin')
    else:
        await state.update_data(min_value=message.text)
        await state.set_state(Coin.max_value)
        await message.answer('Введите максимальное значение в формате "1.8"')


@router.message(Coin.max_value)
async def add_max_value(message: Message, state: FSMContext):
    if convertStr(message.text) == None:
        await message.answer('Не тот формат, давайте заново /choose_coin')
    else:
        await state.update_data(max_value=message.text)
        data = await state.get_data()
        data_source = [
            {'user': message.from_user.username,
             'name': data['name'],
             'min': data['min_value'],
             'max': data['max_value']},
        ]
        Сurrency.insert_many(data_source).execute()
        await message.answer(f'Нажмите, чтобы отслеживать или '
                             'добавить еще монету /choose_coin',
                             reply_markup=kb.track)


@router.callback_query(F.data == 'track')
async def author(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(f'Монеты отслеживаются\n\n'
                                  'Остановить /stop')
    coin_info_list = []
    for users_row in Сurrency.select().where(Сurrency.user == callback.from_user.username):
        coin_info_list.append([users_row.name, users_row.min, users_row.max])

    await state.update_data({'stop_track': True})
    coin_bool_list = [0 for _ in range(len(coin_info_list))]
    full_path = os.path.abspath('./coins.csv')
    while (await state.get_data()).get('stop_track'):
        for row in csv.reader(open(full_path)):
            for item in coin_info_list:
                if row[0] == item[0]:
                    if len(item) < 4:
                        item.append(getCapital(row[1]))
                    else:
                        item[3] == getCapital(row[1])
        for item in coin_info_list:
            if item[3] > item[2]:  # если цена больше максимума
                await callback.message.answer(f'Монета {item[0]} выше максимума'
                                              f' {item[2]}, её цена {item[3]}')
                coin_info_list.remove(item)
                del coin_bool_list[0]
            elif item[3] < item[1]:  # если цена меньше минимума
                await callback.message.answer(f'Монета {item[0]} ниже минимума'
                                              f' {item[1]}, её цена {item[3]}')
                coin_info_list.remove(item)
                del coin_bool_list[0]

        if len(coin_bool_list) == 0:
            await callback.message.answer(f'Больше нечего отслеживать :(\n'
                                          'Удалить монеты /clear_coins\n'
                                          'Добавить монету /choose_coin')
            break
        await asyncio.sleep(randint(3, 90))


@router.message(Command('stop'))
async def stop(message: Message, state: FSMContext):
    await state.update_data({'stop_track': False})
    await message.answer('Бот остановлен')


@router.message(Command('drop_981'))
async def get_coins(message: Message):
    """Cлужебная команда(удаление таблицы)."""
    db.drop_tables(Сurrency)
    await message.answer('ОК')
