from aiogram import types
from aiogram.dispatcher import FSMContext

from config import dp, logger
from db.CRUD.admin import (
    demote_from_admin,
    promote_to_admin,
)
from db.CRUD.player import (
    get_list_of_id_and_names,
    get_player_from_id,
)
from resourses.keyboards import (
    add_admin_keyboard,
)
from resourses.replies import answer
from resourses.states import States


@dp.callback_query_handler(text='settings')
async def settings_menu(call: types.CallbackQuery):
    await dp.bot.send_message(
        chat_id=call.from_user.id,
        text=answer['settings_reply'],
        reply_markup=add_admin_keyboard,
    )
    await call.answer()


@dp.callback_query_handler(text='add_admin')
async def add_admin(call: types.CallbackQuery):
    text = answer['promote_reply'] + await get_list_of_id_and_names('non-admins')
    await dp.bot.send_message(chat_id=call.from_user.id, text=text)
    await States.add_admin.set()
    await call.answer()


@dp.message_handler(state=States.add_admin)
async def add_admin_input(message: types.Message, state: FSMContext):
    try:
        new_admin_id = int(message.text)
        player = await get_player_from_id(new_admin_id)
        await promote_to_admin(new_admin_id)
        await dp.bot.send_message(
            chat_id=message.from_user.id,
            text=answer['promote_complete_reply'].format(player.fullname),
        )
        await dp.bot.send_message(
            chat_id=player.telegram_id,
            text=answer['promote_complete_reply_to_player'].format(
                '@' + message.from_user.username
            ),
        )
        await state.reset_state()
    except ValueError as e:
        await message.answer(answer['value_error_reply'])
        logger.debug(
            answer['value_error_log'], message.from_user.full_name, e, message.text
        )


@dp.callback_query_handler(text='delete_admin')
async def delete_admin(call: types.CallbackQuery):
    text = answer['demote_reply'] + await get_list_of_id_and_names('admins')
    await dp.bot.send_message(chat_id=call.from_user.id, text=text)
    await States.delete_admin.set()
    await call.answer()


@dp.message_handler(state=States.delete_admin)
async def delete_admin_input(message: types.Message, state: FSMContext):
    try:
        admin_id = int(message.text)
        if admin_id != 1:
            player = await get_player_from_id(admin_id)
            await demote_from_admin(admin_id)
            await dp.bot.send_message(
                chat_id=message.from_user.id,
                text=answer['demote_complete_reply'].format(player.fullname),
            )
            await dp.bot.send_message(
                chat_id=player.telegram_id,
                text=answer['demote_complete_reply_to_player'].format(
                    '@' + message.from_user.username
                ),
            )
        else:
            await dp.bot.send_message(chat_id=message.from_user.id, text=answer['demote_error_reply'])

        await state.reset_state()
    except ValueError as e:
        await message.answer(answer['value_error_reply'])
        logger.debug(
            answer['value_error_log'], message.from_user.full_name, e, message.text
        )
