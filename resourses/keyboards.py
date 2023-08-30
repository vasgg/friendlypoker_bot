from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

new_game_admin_keyboard = InlineKeyboardMarkup(row_width=2)
new_game_admin_keyboard.insert(InlineKeyboardButton(text='new game', callback_data='new game'))
new_game_admin_keyboard.insert(InlineKeyboardButton(text='summary', callback_data='summary'))
new_game_admin_keyboard.insert(InlineKeyboardButton(text='settings', callback_data='settings'))

current_game_admin_keyboard = InlineKeyboardMarkup(row_width=2)
current_game_admin_keyboard.insert(InlineKeyboardButton(text='add funds', callback_data='admin add funds'))
current_game_admin_keyboard.insert(InlineKeyboardButton(text='end game', callback_data='end game'))
current_game_admin_keyboard.insert(InlineKeyboardButton(text='settings', callback_data='settings'))

add_funds_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='add 1000', callback_data='self add 1000'),
            InlineKeyboardButton(text='exit game', callback_data='exit game'),
        ]
    ]
)

add_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='add 1000', callback_data='self add 1000')]
    ]
)
add_admin_keyboard = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='add player', callback_data='add_player'),
            InlineKeyboardButton(text='add admin', callback_data='add_admin'),
            InlineKeyboardButton(text='delete admin', callback_data='delete_admin'),
        ],
    ],
)


async def get_paid_button(debt_id):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f'DEBT {debt_id} PAID', callback_data=f'debt_{debt_id}')]])


async def get_paid_button_confirmation(debt_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'YEAH', callback_data=f'{debt_id}_yeah_debt')],
        [InlineKeyboardButton(text=f'NOPE', callback_data=f'{debt_id}_nope_debt')],
    ],
    )
