import json
from typing import Any

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from data_models import *
from config import USER_NAME, PASSWORD, DATA_NAME
import random
from new_word_translate import translate_text

DSN = f'postgresql://{USER_NAME}:{PASSWORD}@localhost:5432/{DATA_NAME}'
engine = sqlalchemy.create_engine(DSN)

create_table(engine)

Session = sessionmaker(bind=engine)
session = Session()

USERS_LIST = []

rwords = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь']
for i, word in enumerate(rwords):
    rword = Rwords(rword=word)
    session.add(rword)
session.commit()

ewords = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october']
for i, word in enumerate(ewords):
    eword = Ewords(eword=word, rword_id=i + 1)
    other_word = Other_words(other_word=word, eword_id=i + 1)
    session.add_all([eword, other_word])
session.commit()


def check_user(id: str) -> bool:
    """
    Функция для проверки существования пользователя в списке пользователей
    :param id: принимает id-пользователя, сторока
    :return: в случае наличия пользователя в списке True, при наличии False
    """
    for u in session.query(Users.user_id):
        USERS_LIST.append(u[0])
    if id not in USERS_LIST:
        return True
    else:
        return False


class New_user():
    """
    Класс для создания нового пользователя
    """

    def __init__(self, id: str, name: str) -> None:
        """
        :param id: получает id пльзователя из id чата
        :param name: получает имя пльзователя из id-чата
        """
        self.id = id
        self.name = name

    def _add_user(self):
        """
        Метод класса New_user, добавляет пользователя в БД, а также слова для изучения
        :return:
        """
        user = Users(user_id=self.id, user_name=self.name)
        session.add(user)
        print(f'Добавлен новый пользователь с id: {self.id}, name: {self.name}')

        for id_rword, rword in enumerate(rwords):
            id_rword += 1
            if (id, id_rword) not in session.query(Users_rwords.user_id, Users_rwords.rword_id).all():
                user_rword = Users_rwords(user_id=self.id, rword_id=id_rword)
                session.add(user_rword)
                print(f'В таблицу user_rword добавлено user_id: {self.id}, rword_id{id_rword}')

        session.commit()

    def get_rwords_list(self) -> str:
        """
        Метод класса New_user, получает слово на русском языке для текущего изучения
        :return: str
        """
        return random.choice((session.query(Rwords.rword)
                              .join(Users_rwords, Rwords.rword_id == Users_rwords.rword_id)
                              .join(Users, Users_rwords.user_id == Users.user_id)
                              .filter(self.id == Users.user_id)
                              .all()))[0]

    def get_target_word(self, word: str) -> str:
        """
        Метод класса New_user, получает перевод изучаемого слова
        :return: str
        """
        return (session.query(Ewords.eword)
                .join(Rwords, Rwords.rword_id == Ewords.rword_id)
                .filter(word == Rwords.rword))[0][0]

    def get_other_words(self, word: str) -> list:
        """
        Метод класса New_user, получает список слов в качестве вариентов для ответа
        :return: list
        """
        list = [w[0] for w in session.query(Other_words.other_word).filter(Other_words.other_word != word).all()]
        return random.sample(list, 3)

    def set_state(self, data: dict) -> None:
        """
        Метод класса New_user, устанавливает состояние для пользователя, преобразовывет
        в json-формат, вносит в БД
        :return: str
        """
        json_data = json.dumps(data)
        user = session.query(Users).filter(Users.user_id == self.id).first()
        user.target_state = json_data
        print(f"Состояние пользователя {self.id} обновлено.")

        session.commit()

    def get_state(self) -> Any:
        """
        Метод класса New_user, получает состояние пользователя из БД, преобразует из json в словарь
        :return: dict / None
        """
        state = session.query(Users).filter(Users.user_id == self.id).first()

        if state and state.target_state:
            print(type(json.loads(state.target_state)))
            return json.loads(state.target_state)

        return None

    def command_add_word(self, word: str) -> int:
        """
        Метод класса New_user, добавляет в БД переданное слово на русском, перевод его на английский,
        подсчитывает количество русских слов в БД
        :return: int
        """
        rword = Rwords(rword=word)
        session.add(rword)
        rword_id = session.query(Rwords.rword_id).filter(Rwords.rword == word)[0][0]

        if (self.id, rword.rword_id) not in session.query(Users_rwords.user_id, Users_rwords.rword_id).all():
            user_rword = Users_rwords(user_id=self.id, rword_id=rword_id)
            session.add(user_rword)

        eng_word = translate_text(word)
        if (eng_word, rword_id) not in session.query(Ewords.eword, Ewords.rword_id).all():
            eword = Ewords(eword=eng_word, rword_id=rword_id)
            session.add(eword)

        eword_id = session.query(Ewords.eword_id).filter(Ewords.eword == eng_word)[0][0]

        if (eng_word, eword_id):
            other_word = Other_words(other_word=eng_word, eword_id=eword_id)
            session.add(other_word)

        session.commit()

        return len(session.query(Ewords.eword, Ewords.rword_id).all())

    def command_delete_word(self, word: str) -> int:
        """
        Метод класса New_user, удаляет переданное слово из БД, возвращает количество изучаемых слов
        :return: int
        """
        w = word.lower()

        rword_record = session.query(Rwords).filter(Rwords.rword == w).first()
        id_rword = rword_record.rword_id

        ewords_records = session.query(Ewords).filter(Ewords.rword_id == id_rword).all()

        for eword_record in ewords_records:
            id_eword = eword_record.eword_id

            other_words_to_delete = session.query(Other_words).filter(Other_words.eword_id == id_eword).all()
            for other_word in other_words_to_delete:
                session.delete(other_word)
            session.delete(eword_record)

        users_rwords_to_delete = session.query(Users_rwords).filter(Users_rwords.rword_id == id_rword).all()
        for user_rword in users_rwords_to_delete:
            session.delete(user_rword)

        session.delete(rword_record)
        session.commit()

        return len(session.query(Ewords.eword, Ewords.rword_id).all())


session.close()
