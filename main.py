import jp
import uvicorn
from db.crud import card_sentence
from util.tool import find_most_match_word
from util.translate import Translate


class Word(jp.Span):
    def __init__(self, **kwargs):
        kwargs['class_'] = 'text-green-500 text-5xl'
        super().__init__(**kwargs)


class WordInput(jp.InputChangeOnly):
    def __init__(self, length=1, **kwargs):
        kwargs['class_'] = 'outline-none bg-gray-300 text-green-500 text-5xl'
        kwargs['style'] = f'width: {length * 2}rem;'
        self.placeholder = kwargs.get('placeholder')
        super().__init__(**kwargs)

    async def temp_placeholder(self, text):
        self.placeholder = text


class Card(jp.Div):
    def __init__(self, **kwargs):
        self.exam_id = None
        self.answer = None
        self.en = None
        self.tw = None
        self.ts = Translate('zh-TW', 'en')
        self.count_index = 0
        self.answer_list = []
        kwargs['class_'] = 'w-2/3 bg-white mt-20  rounded-lg shadow p-12'
        kwargs['style'] = 'min-height: 20rem;'
        super().__init__(**kwargs)

    def get_word(self, sentence, exam):
        ans = find_most_match_word(sentence, exam.word.name)
        return ans

    async def change(self, msg):
        if msg.value.lower() == self.answer.lower():
            await self.build()
            self.count_index = 0
        elif msg.value.strip():
            msg.target.value = ''
            if self.count_index == 0:
                card_sentence.increase_mistake(self.exam_id)
                self.count_index += 1
            await self.make_sound()
            await msg.target.temp_placeholder(self.answer)
        else:
            await self.make_sound()
            msg.target.value = ''

    async def make_sound(self):
        sentence = self.en
        sentence = sentence.replace('"', '')
        eval_text = f"""
            let utterance = new window.SpeechSynthesisUtterance("{sentence}");
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance)
            console.log("{sentence}")
            """
        await self.page.run_javascript(eval_text)

    async def build(self):
        self.delete_components()
        exam = card_sentence.get_exam()
        self.exam_id = exam.id
        sentence = exam.sentence

        en = sentence.en
        tw = sentence.ch
        self.en = en
        self.tw = tw
        word = self.get_word(en, exam)
        self.answer = word
        st_index = en.index(word)
        ed_index = st_index + len(word)
        prefix_s = en[:st_index]
        suffix_s = en[ed_index:]
        self.add_component(Word(text=prefix_s))
        self.add_component(
            WordInput(length=len(word), change=self.change)
        )
        self.add_component(Word(text=suffix_s))
        self.add_component(jp.Div(class_='bg-gray-600 h-px my-6'))
        self.add_component(jp.Div(class_='text-blue-700', text=self.tw))
        self.add_component(jp.Div(class_='bg-gray-600 h-px my-6'))
        self.add_component(jp.Div(class_='text-blue-700', text=self.ts.translate(self.en)))
        self.add_component(jp.Div(class_='bg-gray-600 h-px my-6'))
        self.add_component(jp.Div(class_='text-blue-700', text=f'{exam.word.sound}  /{exam.word.part_of_speech}'))
        self.add_component(jp.Div(class_='bg-gray-600 h-px my-6'))
        self.add_component(jp.Div(class_='text-blue-700', text=exam.explain.en))
        self.add_component(jp.Div(class_='bg-gray-600 h-px my-6'))
        self.add_component(jp.Div(class_='text-blue-700', text=exam.explain.ch))

        print('prefix_s:', prefix_s)
        print('word:', word)
        print('suffix_s:', suffix_s)
        await self.make_sound()


@jp.SetRoute('/')
async def demo():
    wp = jp.justpy_parser_to_wp("""
    <div class="bg-red-200 h-screen">
        <div class="flex flex-col items-center" name="item">
        <Card name="card"></Card>
        </div>
      </div>
    """)
    card = wp.name_dict['card']
    await card.build()

    return wp


app = jp.app

if __name__ == '__main__':
    uvicorn.run('main:app', debug=True)
