"""Модуль групповых хендлеров"""
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.async_telebot import AsyncTeleBot
from utils.logger import log
from utils.database import AdminDatabase
from handlers.admin_configs import get_params_for_message, get_send_procedure

db = AdminDatabase()


def create_markup() -> InlineKeyboardButton:
    """Метод создающий разметку сообщения

    Returns:
        `InlineKeyboardButton`: Разметка сообщения
    """
    message_check_markup = InlineKeyboardMarkup()
    accept_button = InlineKeyboardButton('Принять', callback_data='accept')
    decline_button = InlineKeyboardButton('Отклонить', callback_data='decline')
    message_check_markup.add(accept_button, decline_button)
    return message_check_markup


async def on_message_received(message: Message, bot: AsyncTeleBot):
    """Хендлер срабатывающий на сообщения в чате

    Args:
        `message (Message)`: объект сообщения
        `bot (AsyncTeleBot)`: объект бота
    """
    name = message.from_user.username if message.from_user.username else message.from_user.full_name
    text = message.text if message.text else message.caption
    message_type = message.content_type
    if message.chat.type not in ('group', 'supergroup'):
        return
    log.info('\nmethod: on_message_received\n'
             'Received message: %s from %s, %s', text, name, message.from_user.id)
    log.debug(message)
    if message_type in ('text', 'photo', 'video', 'document'):
        if text:
            text += f'\n\n[{name}](tg://user?id={message.from_user.id})'
        else:
            text = ''

        params = get_params_for_message(text, message)
        #log.debug(params)
        params['reply_markup'] = create_markup()

        for admin in db.admins:
            params['chat_id'] = admin.get('id')
            if params.get('text', None):
                params['text'] = text + f'\n{admin["ps"]}\n'
            elif params.get('caption', None):
                params['caption'] = text + f'\n{admin["ps"]}\n'
            #log.debug(params)
            await get_send_procedure(message_type, bot)(**params)

    await bot.delete_message(message.chat.id, message.id)
    #сохраняем сообщение
    #удаляем сообщение
    #отправляем админам
    