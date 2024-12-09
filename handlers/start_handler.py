from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaDocument, \
    InlineKeyboardButton, ChatMember, ChatMemberUpdated
import time
from states.states import States
from database.db import set_themes, get_themes, del_theme, user_exists, create_new_user, change_active
from keyboards.keyboard import all_themes, exit_btn
from main import db
from main import bot
router = Router()


@router.message(Command('start'))
async def command_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        await bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id,
                                            reply_markup=None)
    except TelegramBadRequest:
        pass

    if not(await user_exists(db, user_id)):
        a = message.date
        b = str(a.date()) + " " + str(a.time())
        await create_new_user(db=db, user_id=user_id, active=True, date=b, first_name=message.from_user.first_name, last_name=message.from_user.last_name, nickname=message.from_user.username)
        await message.answer(
            f"Привет {message.from_user.username}. Это бот для ленты новостей.")
        time.sleep(1)
        await message.answer(
            f"Давайте добавим новую тему в вашу ленту новостей! Введите темы через пробел, по которым вы хотите получать новости")
        await state.set_state(States.wait_for_themes)
    else:
        await message.answer(f"Привет, как дела? Тут скоро будет отвечать нейросеть, если ты уже проходил этот этап")


@router.message(States.wait_for_themes)
async def themes(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(users_themes=message.text)
    await state.set_state(States.wait_for_comfirm_themes)
    themes = message.text.split()
    await set_themes(db, user_id, themes)
    themes = ', '.join(themes)
    await message.answer(f'Ваши темы: {themes}\nВ дальнейшем их можно просмотреть в /themes')


@router.message(Command('themes'))
async def command_themes(message: Message, state: FSMContext):
    user_id = message.from_user.id
    themes = await get_themes(db=db, user_id=user_id)
    kb = all_themes(themes)
    await message.answer(f"Ваши темы. Если хочешь удалить что-то - нажми на нужную кнопку.", reply_markup=kb)
    await state.set_state(States.wait_for_deleting_theme)


@router.callback_query(States.wait_for_deleting_theme)
async def del_themes(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'exit':
        await callback.message.edit_text("Успешно", reply_markup=None)
        await state.clear()
    else:
        user_id = callback.from_user.id
        await del_theme(db=db, user_id=user_id, theme=callback.data)
        themes = await get_themes(db=db, user_id=user_id)
        kb = all_themes(themes)
        await callback.message.edit_text(f"Ваши темы. Если хочешь удалить что-то - нажми на нужную кнопку.", reply_markup=kb)
        await state.set_state(States.wait_for_deleting_theme)

@router.message(Command('suggest'))
async def suggest(message: Message, state: FSMContext):
    await message.answer("Здравствуйте! Если у вас есть какие-либо вопросы, предложения или Вы нашли баги, пожалуйста, напишите мне.\nЯ всегда готов помочь и выслушать Ваше мнение. Спасибо!",reply_markup=exit_btn)
    await state.set_state(States.wait_for_suggest)

@router.message(States.wait_for_suggest)
async def com_themes(message: Message, state: FSMContext):
    from main import bot
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await message.answer(f"Cообщение доставлено", reply_markup=exit_btn)
    await bot.send_message(695088267, f"Сообщение от {message.from_user.full_name}:\n{message.text}")


@router.my_chat_member()
async def my_chat_member(message: ChatMemberUpdated):
    """Проверка на бан бота. Редактирует столбец active"""
    if message.chat.type == 'private':
        if message.new_chat_member.status == 'kicked':
            await change_active(db, message.from_user.id, False)
        elif message.new_chat_member.status == 'member':
            await message.answer("Давно не виделись!")
            await change_active(db, message.from_user.id, True)

