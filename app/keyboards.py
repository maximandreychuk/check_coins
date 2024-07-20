from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           ReplyKeyboardRemove,
                           )
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


track = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отслеживать', callback_data='track')]])
