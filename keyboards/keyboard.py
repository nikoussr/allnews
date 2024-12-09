from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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