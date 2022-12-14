"""Premoderation helpers module."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from telebot.types import Message

if TYPE_CHECKING:
    from bot import Bot


def get_sender_of_message(message: Message):
    """Get sender of message."""
    result = {
        'is_group_or_channel': sender_is_group_or_channel(message),
        'is_user': sender_is_user(message),
    }
    if result['is_group_or_channel']:
        result['chat_id'] = str(message.sender_chat.id)
        result['title'] = message.sender_chat.title
        result['verbose_name'] = message.sender_chat.title.strip()\
            or message.sender_chat.username
    else:
        first_name = message.from_user.first_name or ''
        last_name = message.from_user.last_name or ''
        username = message.from_user.username
        verbose_name = f'{first_name} {last_name}'.strip() or username

        result['chat_id'] = str(message.from_user.id)
        result['verbose_name'] = verbose_name
        result['username'] = username
        result['first_name'] = first_name
        result['last_name'] = last_name

    logging.info("Sender of message: %s (%s)",
                 result['verbose_name'], result['chat_id'])

    return result


def sender_is_group_or_channel(message: Message):
    """Check if sender of message is group or channel."""
    return (message.from_user.is_bot) and (message.sender_chat is not None)


def sender_is_user(message: Message):
    """Check if sender of message is user."""
    return message.from_user and not message.from_user.is_bot


def get_message_text_type(message: Message) -> str:
    """Get message text type"""
    if message.text:
        return "text"
    return "caption"


def get_text_of_message(message: Message) -> str:
    """Get text of message"""
    text_type = get_message_text_type(message)
    if text_type:
        return getattr(message, text_type) or ""
    return ""


def get_html_text_of_message(message: Message) -> str:
    """Get html text of message"""
    text_type = get_message_text_type(message)
    if text_type:
        return getattr(message, f"html_{text_type}") or ""
    return ""


def get_user_link_from_message(message: Message) -> str:
    """Get user link from message"""
    sender = get_sender_of_message(message)
    return get_user_link(sender)


def get_user_link(sender: dict | int, text: None | str = None) -> str:
    """Get user link"""
    text = text or sender['verbose_name']
    chat_id = sender['chat_id'] if isinstance(sender, dict) else sender
    if sender.get('is_user'):
        return f"<a href='tg://user?id={chat_id}'>{text}</a>"
    return text
