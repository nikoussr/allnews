from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import configs

"""Клавиатура для подтверждения"""
y_n_btns = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes'),
     InlineKeyboardButton(text='Нет, я ошибся', callback_data='no')]
])

themes_btns = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Экономика', callback_data='Экономика'),
     InlineKeyboardButton(text='Новости ТПУ', callback_data='Новости ТПУ')]
]

)


def all_themes(themes):
    all_themes = []
    themes_count = 0
    while themes_count < len(themes):
        if len(themes) - themes_count >= 2:
            all_themes.append([InlineKeyboardButton(
                text=themes[themes_count],
                callback_data=themes[themes_count]),
                InlineKeyboardButton(text=themes[themes_count + 1], callback_data=themes[themes_count + 1])])
            themes_count += 2
        else:
            all_themes.append([InlineKeyboardButton(
                text=themes[themes_count],
                callback_data=themes[themes_count])])
            themes_count += 1
    all_themes.append([InlineKeyboardButton(text='⏪ Выйти', callback_data='exit')])
    return InlineKeyboardMarkup(inline_keyboard=all_themes)

exit_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⏪ Выйти', callback_data='exit')]
])


def themes_btn_generator(state):
    themes = list(configs.themes.items())
    all_themes = []
    themes_count = 0
    while themes_count < len(themes):
        if len(all_themes) - themes_count >= 2:
            all_themes.append([InlineKeyboardButton(
                text=themes[themes_count][1],
                callback_data=themes[themes_count][0]),
                InlineKeyboardButton(text=themes[themes_count + 1][1], callback_data=themes[themes_count + 1][0])])
            themes_count += 2
        else:
            all_themes.append([InlineKeyboardButton(
                text=themes[themes_count][1],
                callback_data=themes[themes_count][0])])
            themes_count += 1

    if state == 'exit':
        all_themes.append([InlineKeyboardButton(text='⏪ Выйти', callback_data='exit')])
    elif state == 'continue':
        all_themes.append([InlineKeyboardButton(text='Продолжить ⏭', callback_data='continue')])
    return InlineKeyboardMarkup(inline_keyboard=all_themes)


def update_themes_btn_generator(state, themes_to_del):
    # Получаем список тем из configs и фильтруем его
    themes = list(configs.themes.items())

    # Удаляем темы, которые есть в themes_to_del
    themes = [theme for theme in themes if theme[0] not in themes_to_del]

    all_themes = []
    themes_count = 0

    while themes_count < len(themes):
        if len(all_themes) - themes_count >= 2:
            all_themes.append([
                InlineKeyboardButton(
                    text=themes[themes_count][1],
                    callback_data=themes[themes_count][0]
                ),
                InlineKeyboardButton(
                    text=themes[themes_count + 1][1],
                    callback_data=themes[themes_count + 1][0]
                )
            ])
            themes_count += 2
        else:
            all_themes.append([
                InlineKeyboardButton(
                    text=themes[themes_count][1],
                    callback_data=themes[themes_count][0]
                )
            ])
            themes_count += 1

    if state == 'exit':
        all_themes.append([InlineKeyboardButton(text='⏪ Выйти', callback_data='exit')])
    elif state == 'continue':
        all_themes.append([InlineKeyboardButton(text='Продолжить ⏭', callback_data='continue')])

    return InlineKeyboardMarkup(inline_keyboard=all_themes)
