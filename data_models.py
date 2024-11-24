import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    user_id = sq.Column(sq.BIGINT, primary_key=True, unique=True)
    user_name = sq.Column(sq.VARCHAR(length=30))
    target_state = sq.Column(sq.JSON, nullable=True)

    def __str__(self):
        return f'State = {self.target_state}'


class Rwords(Base):
    __tablename__ = 'rwords'

    rword_id = sq.Column(sq.BIGINT, primary_key=True, autoincrement=True)
    rword = sq.Column(sq.VARCHAR(length=255))

    def __str__(self):
        return f'Слово: {self.rword} с {self.rword_id}'


class Users_rwords(Base):
    __tablename__ = 'users_rwords'

    user_id = sq.Column(sq.BIGINT, sq.ForeignKey('users.user_id'), primary_key=True)
    rword_id = sq.Column(sq.BIGINT, sq.ForeignKey('rwords.rword_id'), primary_key=True)

    user = relationship(Users, backref='users_rwords')
    rword = relationship(Rwords, backref='users_rwords')


class Ewords(Base):
    __tablename__ = 'ewords'

    eword_id = sq.Column(sq.BIGINT, primary_key=True, autoincrement=True)
    eword = sq.Column(sq.VARCHAR(length=50))
    rword_id = sq.Column(sq.Integer, sq.ForeignKey('rwords.rword_id'))

    rword = relationship(Rwords, backref='ewords')

    def __str__(self):
        return f'{self.eword_id}: {self.eword} - {self.rword_id}'


class Other_words(Base):
    __tablename__ = 'other_words'

    other_word_id = sq.Column(sq.BIGINT, primary_key=True, autoincrement=True)
    other_word = sq.Column(sq.VARCHAR(length=50))
    eword_id = sq.Column(sq.Integer, sq.ForeignKey('ewords.eword_id'))

    eword = relationship(Ewords, backref='other_words')


def create_table(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
