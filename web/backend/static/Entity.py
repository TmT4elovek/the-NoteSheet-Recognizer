from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, create_engine, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship, Session

SQLALCHEMY_DATABASE_URL = 'sqlite:///C:\\Users\\nikit\\PycharmProjects\\pythonProject5\\the-NoteSheet-Recognizer\\web\\backend\\music.db' # ссылка на дб


# создание процесса
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


class Base(DeclarativeBase): pass


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)
    password = Column(String(40), nullable=False)
    music_sheets = relationship('MusicSheet', back_populates='user', uselist=True, cascade='all, delete')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MusicSheet(Base):
    __tablename__ = 'music_sheet'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    music_sheet = Column(LargeBinary, nullable=False)
    title = Column(String(70), nullable=False)
    last = Column(Boolean, nullable=False)
    user = relationship('User', back_populates='music_sheets', uselist=False)
    recognized_music_sheet = relationship('RecognizedMusicSheet', back_populates='music_sheet', uselist=False, cascade='all, delete')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class RecognizedMusicSheet(Base):
    __tablename__ = 'recognized_music_sheet'

    id = Column(Integer, primary_key=True)
    recognized_music = Column(LargeBinary, nullable=False)
    sheet_id = Column(Integer, ForeignKey('music_sheet.id'))
    music_sheet = relationship('MusicSheet', back_populates='recognized_music_sheet', uselist=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# создание всех таблиц
#Base.metadata.create_all(engine)