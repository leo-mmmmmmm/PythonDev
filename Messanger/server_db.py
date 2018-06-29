import sys
import datetime
import socket

# Проверим версию SQLAlchemy
try:
    import sqlalchemy
    print('Версия SQLAlchemy: ', sqlalchemy.__version__)
except ImportError:
    print('Библиотека SQLAlchemy не найдена')
    sys.exit(13)

# Чаще используют
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

# Функция declarative_base создаёт базовый класс для декларативной работы
Base = declarative_base()


friendship = Table(
    'friendships', Base.metadata,
    Column('friend_a_id', Integer, ForeignKey('Users.id'),
                                        primary_key=True),
    Column('friend_b_id', Integer, ForeignKey('Users.id'),
                                        primary_key=True)
)


# На основании базового класса можно создавать необходимые классы
class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    name = Column(String)
    last_name = Column(String)
    description = Column(String)

    friends = relationship("User", secondary=friendship,
                           primaryjoin=id == friendship.c.friend_a_id,
                           secondaryjoin=id == friendship.c.friend_b_id,
                           )

    def __init__(self, login, password, name = '', last_name='', description=''):
        self.login = login
        self.password = password
        self.name = name
        self.last_name = last_name
        self.description = description

    def __repr__(self):
        return f'User({ self.login }, { self.password }, { self.name }, { self.last_name }, { self.description })'


class UserHistory(Base):
    __tablename__ = 'History'
    id = Column(Integer, primary_key=True)
    login_date = Column(String)
    ip_address = Column(String)

    user_id = Column(Integer, ForeignKey(User.id))
    User = relationship('User', back_populates='UserHistory')

    def __init__(self, login_date, ip_address, user_id):
        self.user_id = user_id
        self.login_date = login_date
        self.ip_address = ip_address

    def __repr__(self):
        return f'UserHistory({ self.date }, { self.ip_address })'

User.UserHistory = relationship('UserHistory', order_by=UserHistory.id, back_populates='User')

friendship_union = select([
                        friendship.c.friend_a_id,
                        friendship.c.friend_b_id
                        ]).union(
                            select([
                                friendship.c.friend_b_id,
                                friendship.c.friend_a_id]
                            )
                    ).alias()
User.all_friends = relationship('User',
                       secondary=friendship_union,
                       primaryjoin=User.id==friendship_union.c.friend_a_id,
                       secondaryjoin=User.id==friendship_union.c.friend_b_id,
                       viewonly=True)

# Создание таблицы
engine = create_engine('sqlite:///users_db.sqlite', echo=False)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
