import jp
import uvicorn
from util.translate import Translate
import re


class Word(jp.Span):
    def __init__(self, **kwargs):
        kwargs['class_'] = 'text-green-500 text-xl pr-2 cursor-pointer'
        kwargs['on_mouseover'] = self.on_mouse_enter
        kwargs['on_click'] = self.on_mouse_enter
        self.is_green = True
        super().__init__(**kwargs)

    async def on_mouse_enter(self, _):
        if self.is_green:
            self.set_class('text-gray-500')
        else:
            self.set_class('text-green-500')

        self.is_green = not self.is_green


class Watchcard(jp.Div):
    html_render = """
    <div class="w-2/3 bg-white mt-20  rounded-lg shadow p-12" style="min-height: 20rem;">
    <textarea rows="4" cols="50" name="textarea"></textarea>
    <button class="text-5xl px-6 m-2 text-lg text-indigo-100 transition-colors duration-150 bg-indigo-700 rounded-lg focus:shadow-outline hover:bg-indigo-80" @click="click">送出</button>
    </div>
    """

    async def click(self, _):
        textarea = self.name_dict['textarea']
        if textarea.value:
            self.page.original_english = textarea.value
        item = self.page.name_dict['item']
        item.delete()
        card = Card()
        self.page.card = card
        item.add_component(card)
        card.init_sentence()
        await card.build()


class Card(jp.Div):
    def __init__(self, **kwargs):
        self.span_list = []
        kwargs['class_'] = 'w-2/3 bg-white mt-20  rounded-lg shadow p-12 flex flex-wrap'
        kwargs['style'] = 'min-height: 20rem;'
        super().__init__(**kwargs)
        self.en_area = None
        self.tw_area = None
        self.sentence_list = []

        self.ts = Translate('zh-TW', 'en')

    async def make_sound(self, target):
        eval_text = f"""
            let utterance = new window.SpeechSynthesisUtterance("{target.replace('"', '')}");
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance)
            console.log("{target}")
            """
        await self.page.run_javascript(eval_text)

    async def change_area_text(self, english):
        self.en_area.value = english
        self.tw_area.text = self.ts.translate(english)
        await self.make_sound(english)

    async def click(self, _):
        await self.rebuild()

    async def build(self):
        self.delete_components()
        self.span_list = []
        sentence = self.sentence_list.pop(0)
        for word in sentence.split():
            el = Word(text=word)
            self.add_component(el)
            self.span_list.append(el)

        self.add_component(jp.Button(text='更新', click=self.click))
        self.add_component(jp.Div(class_='bg-gray-600 h-px my-6 w-full'))
        self.en_area = jp.Textarea(class_='w-full')
        self.add_component(jp.Button(text='更新', click=self.click_to_build))
        self.add_component(self.en_area)
        self.add_component(jp.Div(class_='bg-gray-600 h-px my-6 w-full'))
        self.tw_area = jp.Div()
        self.add_component(self.tw_area)

        await self.change_area_text(sentence)

    async def click_to_build(self, _):
        await self.build()

    async def rebuild(self):
        words = []
        for el in self.span_list:
            if el.is_green:
                words.append(el.text)
        await self.change_area_text(" ".join(words))

    def init_sentence(self):
        for sentence in re.split(r'[\.!?]', self.page.original_english):
            if sentence:
                self.sentence_list.append(sentence)


@jp.SetRoute('/')
async def demo():
    wp = jp.justpy_parser_to_wp("""
    <div class="bg-red-200 h-screen">
        <div class="flex flex-col items-center" name="item">
        <WatchCard></WatchCard>
        </div>
      </div>
    """)

    return wp


app = jp.app

if __name__ == '__main__':
    uvicorn.run('articles:app', debug=True)
