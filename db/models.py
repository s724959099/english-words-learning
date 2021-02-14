from pony.orm import Required, Set, Optional, show, db_session, select, Database, PrimaryKey
from pydantic import BaseModel, Field
import datetime
import json
import os

db = Database()


class Word(db.Entity):
    name = Optional(str, nullable=True, unique=True)
    part_of_speech = Optional(str, nullable=True)
    sound = Optional(str, nullable=True)
    explain = Set('Explain', lazy=True, cascade_delete=True)
    exam = Set('Exam', lazy=True, cascade_delete=True)


class Explain(db.Entity):
    word = Optional(Word, reverse='explain')
    en = Optional(str, nullable=True)
    ch = Optional(str, nullable=True)
    sentence = Set('Sentence', lazy=True, cascade_delete=True)
    exam = Set('Exam', lazy=True, cascade_delete=True)


class Sentence(db.Entity):
    explain = Optional(Explain, reverse='sentence')
    en = Optional(str, nullable=True)
    ch = Optional(str, nullable=True)
    exam = Set('Exam', lazy=True, cascade_delete=True)


class Exam(db.Entity):
    word = Optional(Word, reverse='exam')
    explain = Optional(Explain, reverse='exam')
    sentence = Optional(Sentence, reverse='exam')
    created_at = Required(datetime.datetime, default=datetime.datetime.now)
    appear_cout = Required(int, default=1)


class Url(db.Entity):
    href = Required(str, unique=True)
    read = Required(bool, default=False)


db.bind(provider='sqlite', filename='db.sqlite3', create_db=True)
db.generate_mapping(create_tables=True)

if __name__ == '__main__':
    print(Word.select(lambda x: x.name == 'guilty').count())
