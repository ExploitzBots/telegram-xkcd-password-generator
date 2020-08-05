#!venv/bin/python
# TODO: Make CAPITALIZATION configurable

import config
import logging
from typing import Dict
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.callback_data import CallbackData
import dbworker
import pwdgen
from utils import get_language
from texts import strings

bot = Bot(token=config.token, parse_mode="HTML")
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


cb_wordcount = CallbackData("word", "change")
cb_prefixes = CallbackData("prefixes", "action")
cb_separators = CallbackData("separators", "action")


def make_settings_keyboard_for_user(user_id, lang_code):
    """
    Prepare keyboard for user based on his settings

    :param user_id: User ID in Telegram
    :param lang_code: User's language code
    :return: Inline Keyboard object
    """
    user = dbworker.get_person(user_id)
    kb = types.InlineKeyboardMarkup()

    wrds_lst = []
    if user["word_count"] >= (config.length_min + 1):
        wrds_lst.append(types.InlineKeyboardButton(text=strings.get(get_language(lang_code)).get("minusword"),
                                                   callback_data=cb_wordcount.new(change="minus")))
    if user["word_count"] <= (config.length_max - 1):
        wrds_lst.append(types.InlineKeyboardButton(text=strings.get(get_language(lang_code)).get("plusword"),
                                                   callback_data=cb_wordcount.new(change="plus")))
    kb.add(*wrds_lst)

    if user["prefixes"]:
        kb.add(types.InlineKeyboardButton(text=strings.get(get_language(lang_code)).get("minuspref"),
                                          callback_data=cb_prefixes.new(action="disable")))
    else:
        kb.add(types.InlineKeyboardButton(text=strings.get(get_language(lang_code)).get("pluspref"),
                                          callback_data=cb_prefixes.new(action="enable")))

    if user["separators"]:
        kb.add(types.InlineKeyboardButton(text=strings.get(get_language(lang_code)).get("minussep"),
                                          callback_data=cb_separators.new(action="disable")))
    else:
        kb.add(types.InlineKeyboardButton(text=strings.get(get_language(lang_code)).get("plussep"),
                                          callback_data=cb_separators.new(action="enable")))
    return kb


def make_regenerate_keyboard(lang_code):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text=strings.get(get_language(lang_code)).get("regenerate"),
                                     callback_data="regenerate")
    keyboard.add(btn)
    return keyboard


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(strings.get(get_language(message.from_user.language_code)).get("start"))


@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    await message.answer(strings.get(get_language(message.from_user.language_code)).get("help"))


@dp.message_handler(commands=["settings"])
async def cmd_settings(message: types.Message):
    await message.answer(text=dbworker.get_settings_text(message.chat.id, message.from_user.language_code),
                         reply_markup=make_settings_keyboard_for_user(message.chat.id, message.from_user.language_code))


@dp.message_handler(commands=["generate"])
async def cmd_generate_custom(message: types.Message):
    await message.answer(text=f"<code>{pwdgen.generate_custom(message.chat.id)}</code>",
                         reply_markup=make_regenerate_keyboard(message.from_user.language_code))


@dp.message_handler(commands=["generate_weak"])
async def cmd_generate_weak_password(message: types.Message):
    await message.answer(f"<code>{pwdgen.generate_weak_pwd()}</code>")


@dp.message_handler(commands=["generate_normal"])
async def cmd_generate_normal_password(message: types.Message):
    await message.answer(f"<code>{pwdgen.generate_normal_pwd()}</code>")


@dp.message_handler(commands=["generate_strong"])
async def cmd_generate_strong_password(message: types.Message):
    await message.answer(f"<code>{pwdgen.generate_strong_pwd()}</code>")


@dp.message_handler(commands=["generate_stronger"])
async def cmd_generate_stronger_password(message: types.Message):
    await message.answer(f"<code>{pwdgen.generate_stronger_pwd()}</code>")


@dp.message_handler(commands=["generate_insane"])
async def cmd_generate_insane_password(message: types.Message):
    await message.answer(f"<code>{pwdgen.generate_insane_pwd()}</code>")


@dp.message_handler()  # Default messages handler
async def default(message: types.Message):
    await cmd_generate_strong_password(message)


@dp.callback_query_handler(lambda call: call.data == "regenerate")
async def regenerate(call: types.CallbackQuery):
    await call.message.edit_text(text=f"<code>{pwdgen.generate_custom(call.from_user.id)}</code>",
                                 reply_markup=make_regenerate_keyboard(call.from_user.language_code))
    await call.answer()


@dp.callback_query_handler(cb_wordcount.filter())
async def change_wordcount(call: types.CallbackQuery, callback_data: Dict[str, str]):
    if callback_data["change"] == "minus":
        dbworker.change_word_count(call.from_user.id, increase=False)
    elif callback_data["change"] == "plus":
        dbworker.change_word_count(call.from_user.id, increase=True)
    else:
        return

    await call.message.edit_text(text=dbworker.get_settings_text(call.from_user.id, call.from_user.language_code),
                                 reply_markup=make_settings_keyboard_for_user(call.from_user.id, call.from_user.language_code))
    await call.answer()


@dp.callback_query_handler(cb_prefixes.filter())
async def toggle_prefixes(call: types.CallbackQuery, callback_data: Dict[str, str]):
    if callback_data["action"] == "disable":
        dbworker.change_prefixes(call.from_user.id, enable_prefixes=False)
    elif callback_data["action"] == "enable":
        dbworker.change_prefixes(call.from_user.id, enable_prefixes=True)
    else:
        return

    await call.message.edit_text(text=dbworker.get_settings_text(call.from_user.id, call.from_user.language_code),
                                 reply_markup=make_settings_keyboard_for_user(call.from_user.id, call.from_user.language_code))
    await call.answer()


@dp.callback_query_handler(cb_separators.filter())
async def toggle_separators(call: types.CallbackQuery, callback_data: Dict[str, str]):
    if callback_data["action"] == "disable":
        dbworker.change_separators(call.from_user.id, enable_separators=False)
    elif callback_data["action"] == "enable":
        dbworker.change_separators(call.from_user.id, enable_separators=True)
    else:
        return

    await call.message.edit_text(text=dbworker.get_settings_text(call.from_user.id, call.from_user.language_code),
                                 reply_markup=make_settings_keyboard_for_user(call.from_user.id, call.from_user.language_code))
    await call.answer()


@dp.inline_handler()  # Default inline mode handler
async def inline(query: types.InlineQuery):
    results = [
        types.InlineQueryResultArticle(
            id="1",
            title="Insane password",
            description="2 prefixes, 2 suffixes, 3 words, separated by the same (random) symbol",
            input_message_content=types.InputTextMessageContent(
                message_text=f"<code>{pwdgen.generate_insane_pwd()}</code>"
            ),
            thumb_url="https://raw.githubusercontent.com/MasterGroosha/telegram-xkcd-password-generator/master/img/pwd_green.png",
            thumb_height=64,
            thumb_width=64,
        ),

        types.InlineQueryResultArticle(
            id="2",
            title="Very strong password",
            description="4 words, random uppercase, separated by numbers",
            input_message_content=types.InputTextMessageContent(
                message_text=f"<code>{pwdgen.generate_stronger_pwd()}</code>"
            ),
            thumb_url="https://raw.githubusercontent.com/MasterGroosha/telegram-xkcd-password-generator/master/img/pwd_green.png",
            thumb_height=64,
            thumb_width=64,
        ),

        types.InlineQueryResultArticle(
            id="3",
            title="Strong password",
            description="3 words, random uppercase, separated by numbers",
            input_message_content=types.InputTextMessageContent(
                message_text=f"<code>{pwdgen.generate_strong_pwd()}</code>"
            ),
            thumb_url="https://raw.githubusercontent.com/MasterGroosha/telegram-xkcd-password-generator/master/img/pwd_yellow.png",
            thumb_height=64,
            thumb_width=64,
        ),

        types.InlineQueryResultArticle(
            id="4",
            title="Normal password",
            description="3 words, second one is uppercase",
            input_message_content=types.InputTextMessageContent(
                message_text=f"<code>{pwdgen.generate_normal_pwd()}</code>"
            ),
            thumb_url="https://raw.githubusercontent.com/MasterGroosha/telegram-xkcd-password-generator/master/img/pwd_yellow.png",
            thumb_height=64,
            thumb_width=64,
        ),

        types.InlineQueryResultArticle(
            id="5",
            title="Weak password",
            description="2 words, no digits",
            input_message_content=types.InputTextMessageContent(
                message_text=f"<code>{pwdgen.generate_weak_pwd()}</code>"
            ),
            thumb_url="https://raw.githubusercontent.com/MasterGroosha/telegram-xkcd-password-generator/master/img/pwd_red.png",
            thumb_height=64,
            thumb_width=64,
        )
    ]
    await query.answer(results=results, cache_time=1, is_personal=True)


if __name__ == '__main__':
    # aiogram's polling is MUCH better than pyTelegramBotAPI's, so we can simply use it.
    executor.start_polling(dp, skip_updates=True)
