from models import Exam, Explain, select, Sentence, db_session
from pony.orm import commit
import random
import datetime
from addict import Dict


class CardSentence:

    def _get_query_random(self, query):
        count = query.count() - 1
        idx = random.randint(0, count)
        return query[idx:idx + 1][0]

    # noinspection PyChainedComparisons
    @db_session
    def _get_old_in_time_exam(self):
        now = datetime.datetime.now()
        before_now_5min = now - datetime.timedelta(minutes=5)
        before_now_1day = now - datetime.timedelta(days=1)
        query1 = Exam.select(
            lambda x:
            x.created_at <= before_now_5min and
            (x.mistake > 0 or x.appear_count == 1)
        )
        before_now_2day = now - datetime.timedelta(days=2)
        query2 = Exam.select(
            lambda x:
            before_now_2day <= x.created_at and x.created_at <= before_now_1day and
            (x.mistake > 0 or x.appear_count <= 2)
        )
        before_now_4day = now - datetime.timedelta(days=4)
        query3 = Exam.select(
            lambda x:
            before_now_4day <= x.created_at and x.created_at <= before_now_2day and
            (x.mistake > 0 or x.appear_count <= 3)
        )
        before_now_7day = now - datetime.timedelta(days=7)
        query4 = Exam.select(
            lambda x:
            before_now_7day <= x.created_at and x.created_at <= before_now_4day and
            (x.mistake > 0 or x.appear_count <= 4)
        )
        before_now_15day = now - datetime.timedelta(days=15)
        query5 = Exam.select(
            lambda x:
            before_now_15day <= x.created_at and x.created_at <= before_now_7day and
            (x.mistake > 0 or x.appear_count <= 5)
        )

        query6 = Exam.select(
            lambda x:
            before_now_15day > x.created_at and
            (x.mistake > 0 or x.appear_count <= 6)
        )
        query = query1 or query2 or query3 or query4 or query5 or query6
        if query.count():
            exam = self._get_query_random(query)
            exam.appear_count += 1
            if exam.mistake:
                exam.mistake -= 1
            commit()
            return exam

    @db_session
    def increase_mistake(self, exam_id):
        exam = Exam.get(id=exam_id)
        exam.mistake += 1
        commit()
        return exam

    def exam_to_dict(self, exam):
        sentence = exam.sentence
        word = exam.word
        explain = exam.explain
        ret = exam.to_dict()
        ret['sentence'] = sentence.to_dict()
        ret['word'] = word.to_dict()
        ret['explain'] = explain.to_dict()
        return Dict(ret)

    @db_session
    def get_exam(self):
        exam = self._get_old_in_time_exam()
        if exam:
            return self.exam_to_dict(exam)
        ids_query = select(el.explain.id for el in Exam)
        while True:
            try:
                query = Explain.select(lambda x: x.id not in ids_query)
                explain = self._get_query_random(query)
                sentence = self._get_query_random(Sentence.select(lambda x: x.explain == explain))
                exam_query = Exam.select(lambda x: x.sentence == sentence)
                if exam_query.count():
                    exam = exam_query.first()
                    exam.appear_cout += 1
                else:

                    exam = Exam(
                        word=explain.word,
                        explain=explain,
                        sentence=sentence
                    )
                return self.exam_to_dict(exam)
            except Exception:
                pass


card_sentence = CardSentence()
if __name__ == '__main__':
    import time

    print('start')
    st = time.time()
    sentence = card_sentence.get_exam()
    ed = time.time()
    print('end')
    print(ed - st)
    print()
