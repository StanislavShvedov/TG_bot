import json
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from data_models import *
from config import USER_NAME, PASSWORD, DATA_NAME
import random

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

ewords = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
for i, word in enumerate(ewords):
    eword = Ewords(eword=word, rword_id=i+1)
    other_word = Other_words(other_word=word, eword_id=i+1)
    session.add_all([eword, other_word])
session.commit()

def check_user(id):
    for u in session.query(Users.user_id):
        USERS_LIST.append(u[0])
    if id not in USERS_LIST:
        return True
    else:
        return False

def add_new_user(id, name):

    user = Users(user_id=id, user_name=name)
    session.add(user)
    print(f'Добавлен новый пользователь с id: {id}, name: {name}')

    for id_rword, rword in enumerate(rwords):
        id_rword += 1
        if (id, id_rword) not in session.query(Users_rwords.user_id, Users_rwords.rword_id).all():
            user_rword = Users_rwords(user_id=id, rword_id=id_rword)
            session.add(user_rword)
            print(f'В таблицу user_rword добавлено user_id: {id}, rword_id{id_rword}')

    session.commit()

def get_rwords_list(id):
    return random.choice((session.query(Rwords.rword)
            .join(Users_rwords, Rwords.rword_id == Users_rwords.rword_id)
            .join(Users, Users_rwords.user_id == Users.user_id)
            .filter(id == Users.user_id)
            .all()))[0]

def get_target_word(word):
    return (session.query(Ewords.eword)
            .join(Rwords, Rwords.rword_id == Ewords.rword_id)
            .filter(word == Rwords.rword))[0][0]

def get_other_words(word):
    list = [w[0] for w in session.query(Other_words.other_word).filter(Other_words.other_word != word).all()]
    return random.sample(list, 3)

def set_state(id, data):
    json_data = json.dumps(data)
    user = session.query(Users).filter(Users.user_id == id).first()
    user.target_state = json_data
    print(f"Состояние пользователя {id} обновлено.")

    session.commit()

def get_state(id):
    state = session.query(Users).filter(Users.user_id == id).first()

    if state and state.target_state:
        return json.loads(state.target_state)

    return None

def command_add_word(id, word):
    print('Here command_add_word(id, word):')
    rword = Rwords(rword=word)
    session.add(rword)
    rword_id = session.query(Rwords.rword_id).filter(Rwords.rword == word)[0][0]
    if (id, rword.rword_id) not in session.query(Users_rwords.user_id, Users_rwords.rword_id).all():
        user_rword = Users_rwords(user_id=id, rword_id=rword_id)
        session.add(user_rword)
        print(f'В таблицу rwords добавлено user_id: {id}, rword_id{rword}')
    session.commit()

session.close()