from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaDocument, \
    InlineKeyboardButton, ChatMember, ChatMemberUpdated
import time

import configs
import keyboards.keyboard
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

    if not (await user_exists(db, user_id)):
        a = message.date
        b = str(a.date()) + " " + str(a.time())
        await create_new_user(db=db, user_id=user_id, active=True, date=b, first_name=message.from_user.first_name,
                              last_name=message.from_user.last_name, nickname=message.from_user.username)
        await message.answer(
            f"Привет {message.from_user.username}. Это бот для ленты новостей.")
        time.sleep(1)
        await message.answer(
            f"Давайте добавим новые темы в Вашу ленту новостей! Нажимайте на кнопку, если вас это интересует.\nЕсли вы выбрали свои темы, то нажмите 'Продолжить'",
            reply_markup=keyboards.keyboard.themes_btn_generator('continue'))
        await state.set_state(States.wait_for_themes)
    else:
        await message.answer(f"Привет, как дела? Тут скоро будет отвечать нейросеть, если ты уже проходил этот этап")


@router.callback_query(States.wait_for_themes)
async def add_themes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    themes = data.get('selected_themes', [])
    selected_theme = callback.data
    if selected_theme == 'continue':
        data = await state.get_data()
        themes = data.get('selected_themes', [])
        user_id = callback.from_user.id
        try:
            # Вставляем выбранные темы в базу данных
            await set_themes(db, user_id, themes)
            await callback.answer("Темы успешно сохранены!")
            await callback.message.edit_text(f"Отлично! Теперь можете ждать новости))", reply_markup=None)
        except Exception as e:
            print(f"Ошибка при сохранении тем: {e}")
            await callback.answer("Произошла ошибка при сохранении тем.")
    else:
        if selected_theme not in themes:
            themes.append(selected_theme)

        await state.update_data(selected_themes=themes)

        themes_text = "\n".join(configs.themes[theme] for theme in themes)

        await callback.message.edit_text(
            f"Вы выбрали темы:\n{themes_text}",
            reply_markup=keyboards.keyboard.update_themes_btn_generator('continue', themes)
        )

        await state.set_state(States.wait_for_themes)


@router.message(Command('themes'))
async def command_themes(message: Message, state: FSMContext):
    user_id = message.from_user.id
    themes = await get_themes(db=db, user_id=user_id)
    themes = [configs.themes[theme] for theme in themes]
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
        themes = [configs.themes[theme] for theme in themes]
        kb = all_themes(themes)
        await callback.message.answer(f"Ваши темы. Если хочешь удалить что-то - нажми на нужную кнопку.", reply_markup=kb)
        await state.set_state(States.wait_for_deleting_theme)


@router.message(Command('add'))
async def add_theme_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        # Извлекаем текущие темы пользователя
        user_themes = await db.fetch('SELECT theme FROM themes WHERE user_id = $1', user_id)
        user_themes_set = {record['theme'] for record in user_themes}

        # Получаем все доступные темы из вашего модуля с темами
        all_themes = set(configs.themes.keys())

        # Определяем темы, которых нет у пользователя
        available_themes = all_themes - user_themes_set

        if not available_themes:
            await message.answer("У вас уже есть все доступные темы!")
            return

        await message.answer("Выберите тему для добавления:",
                             reply_markup=keyboards.keyboard.update_themes_btn_generator('continue', user_themes_set))

        # Сохраняем состояние, чтобы знать, что пользователь выбирает тему
        await state.set_state(States.wait_for_add_theme)

    except Exception as e:
        print(f"Ошибка при получении тем: {e}")
        await message.answer("Произошла ошибка при получении тем.")


@router.callback_query(States.wait_for_add_theme)
async def add_selected_theme(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    selected_theme = callback.data
    try:
        # Добавляем выбранную тему в базу данных
        await db.execute('INSERT INTO themes(user_id, theme) VALUES($1, $2)', user_id, selected_theme)
        await callback.answer(f"Тема '{configs.themes[selected_theme]}' успешно добавлена!")
    except Exception as e:
        print(f"Ошибка при добавлении темы: {e}")
        await callback.answer("Произошла ошибка при добавлении темы.")

    user_themes = await db.fetch('SELECT theme FROM themes WHERE user_id = $1', user_id)
    user_themes_set = {record['theme'] for record in user_themes}
    """
        # Получаем все доступные темы
        all_themes = set(configs.themes.keys())
    
        # Определяем доступные темы для добавления
        available_themes = all_themes - user_themes_set
    
        if not available_themes:
            await callback.message.answer("У вас уже есть все доступные темы!")
            await state.clear()
            return"""

    await callback.message.edit_text(f"Выберите тему для добавления:",
                                     reply_markup=keyboards.keyboard.update_themes_btn_generator('continue',
                                                                                                 user_themes_set))
    await state.set_state(States.wait_for_add_theme)





@router.message(Command('suggest'))
async def suggest(message: Message, state: FSMContext):
    await message.answer(
        "Здравствуйте! Если у вас есть какие-либо вопросы, предложения или Вы нашли баги, пожалуйста, напишите мне.\nЯ всегда готов помочь и выслушать Ваше мнение. Спасибо!",
        reply_markup=exit_btn)
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
