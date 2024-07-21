from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           ReplyKeyboardRemove,
                           )
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


track = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отслеживать', callback_data='track')]])

three = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='3', callback_data='three')]])
