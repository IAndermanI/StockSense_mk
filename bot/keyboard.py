from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_inlineKB_from_list(callback, items, return_markup=True):
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(text=f"{item}", callback_data=f"{callback}_{item}")
    builder.adjust(2)
    return builder.as_markup() if return_markup else builder
