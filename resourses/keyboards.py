from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

new_game_admin_keyboard = InlineKeyboardMarkup(row_width=2)
new_game_admin_keyboard.insert(InlineKeyboardButton(text='new game', callback_data='new game'))
new_game_admin_keyboard.insert(InlineKeyboardButton(text='summary', callback_data='summary'))
new_game_admin_keyboard.insert(InlineKeyboardButton(text='settings', callback_data='settings'))

current_game_admin_keyboard = InlineKeyboardMarkup(row_width=2)
current_game_admin_keyboard.insert(InlineKeyboardButton(text='add funds', callback_data='admin add funds'))
current_game_admin_keyboard.insert(InlineKeyboardButton(text='end game', callback_data='end game'))
current_game_admin_keyboard.insert(InlineKeyboardButton(text='settings', callback_data='settings'))

add_funds_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='add 1000', callback_data='self add 1000'),
                                                            InlineKeyboardButton(text='exit game', callback_data='exit game')]])

add_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='add 1000', callback_data='self add 1000')]])
