"""Модуль предназначенный для работы с базой данных"""
from pathlib import Path
from typing import Dict, List

from tinydb import Query, TinyDB
from tinydb.storages import MemoryStorage

from utils.logger import log

admin = Query()
memory = TinyDB(storage=MemoryStorage)

# Create db directory and database files if not exists
Path("db").mkdir(parents=True, exist_ok=True)


class AdminDatabase():
    """Класс представляюший объект базы администраторов."""

    def __init__(self, **kwargs):
        self.__db = TinyDB(kwargs.pop('db', 'db/admins.json'), encoding='utf8')

    @property
    def admins(self) -> List[Dict]:
        """Поле представляющее список администраторов.

        Returns:
            List[Dict]: Список документов администраторов.
        """
        log.info('Вызван список администраторов!')
        return self.__db.all()

    @admins.setter
    def admins(self, value: Dict):
        """Сеттер поля администраторов, позволяющий добавлять документы в базу."""
        self.add_admin(**value)

    def add_admin(self, username: str, fullname: str, user_id: int, sign: str):
        """Метод позволяющий добавлять администраторов в базу."""
        _ = self.__db.insert({
            'id': int(user_id),
            'username': username,
            'fullname': fullname,
            'sign': sign
        })
        log.info('Запись администратора успешно добавлена! Id: %s.', str(_))

    def update(self, admin_id: int, query: Dict):
        """Метод позволяющий обновить записи в базе.

        Args:
            `admin_id (int)`: ID администратора.
            `query (Dict)`: Запись изменений.
        """
        self.__db.update(query, admin.id == admin_id)

    def remove_admin(self, **kwargs):
        """Метод позволяющий удалять администраторов из базы."""
        if kwargs.get('username'):
            _ = self.__db.remove(admin.username == kwargs.get('username'))
        elif kwargs.get('fullname'):
            _ = self.__db.remove(admin.fullname == kwargs.get('fullname'))
        elif kwargs.get('id'):
            _ = self.__db.remove(admin.id == int(kwargs.get('id')))
        log.info('Администратор удален! Id: %s.', str(_))

    def get_admin_by_id(self, admin_id: int) -> Dict:
        """Метод позволяющий получить администратора по его ID.

        Args:
            `id (int)`: ID администратора.

        Returns:
            Dict: Документ администратора.
        """
        return self.__db.get(admin.id == admin_id)


tag = Query()


class TagDatabase():
    """Класс представляюший объект базы тегов."""

    def __init__(self, **kwargs):
        self.__db = TinyDB(kwargs.pop('db', 'db/tags.json'), encoding='utf8')

    @property
    def tags(self) -> List[Dict]:
        """Поле представляющее список тегов.

        Returns:
            `List[Dict]`: Список документов тегов.
        """
        log.info('Вызван список тегов!')
        return self.__db.all()

    @tags.setter
    def tags(self, value: str):
        """Сеттер поля тегов, позволяющий добавлять документы в базу."""
        _ = self.__db.insert({'tag': value})
        log.info('Тег успешно добавлен! Id: %s.', str(_))

    def remove_tag(self, value: str):
        """Метод позволяющий удалять теги из базы."""
        _ = self.__db.remove(tag.tag == value)
        log.info('Тег удален! Id: %s.', str(_))


unmarked_massage = Query()


class UnmarkedMessages():
    """Класс неразмеченных "новых" сообщений."""

    def __init__(self, **kwargs) -> None:
        self.__db = TinyDB(kwargs.pop(
            'db', 'db/unmarked_messages.json'), encoding='utf8')
        self.states = ['NEW', 'IN_PROCESS', 'DONE']

    @property
    def messages(self) -> List[Dict]:
        """Поле представляющее список сообщений."""
        return self.__db.all()

    @messages.setter
    def messages(self, value: Dict):
        """Сеттер поля сообщений, позволяющий добавлять документы в базу."""
        self.__db.insert({
            'message_type': value.pop('message_type'),
            'uid': value.pop('uid'),  # 'chat_id!message_id'
            'message_id': value.pop('message_id'),
            'chat_id': value.pop('chat_id'),
            'text': value.pop('text', None),
            'caption': value.pop('caption', None),
            'photo': value.pop('photo', None),
            'video': value.pop('video', None),
            'audio': value.pop('audio', None),
            'sender_id': value.pop('sender_id'),
            'state': value.pop('state', 'NEW'),
            'sended_to': value.pop('sended_to', None),
        })

    def remove_message(self, uid: str):
        """Метод позволяющий удалять сообщений из базы."""
        _ = self.__db.remove_message(unmarked_massage.uid == uid)
        log.info('Сообщение удалено! Id: %s.', _)

    def next_state(self, uid: str):
        """Метод позволяющий перейти к следующему состоянию сообщения."""
        cur_state = self.__db.search(unmarked_massage.uid == uid)['start']
        if cur_state == 'DONE':
            log.warning('Сообщение уже в финальном статусе! Удаляю…')
            self.remove_message(uid)
        else:
            new_state = self.states[self.states.index('cur_state')+1]
            self.__db.update({
                'state': new_state
            }, unmarked_massage.uid == uid)
            log.info('Состояние изменено! Новое состояние: {new_state}')

    def set_state(self, uid: str, state: str):
        """Метод позволяющий задать необходимое состояние сообщения."""
        if not state in self.states:
            log.error(
                'Указанное состояние не соответствует ни одному из возможных!')
            return

        self.__db.update({
            'state': state
        }, unmarked_massage.uid == uid)
