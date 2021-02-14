import requests
from pyquery import PyQuery as pq
from db import models
from loguru import logger
from pony.orm import flush


@models.db_session
def crawl_word(url):
    if not (url.startswith('http') and '://' in url):
        url = f'https://dictionary.cambridge.org/zht/%E8%A9%9E%E5%85%B8/%E8%8B%B1%E8%AA%9E-%E6%BC%A2%E8%AA%9E-%E7%B9%81%E9%AB%94/{url}'
    if models.Url.select(lambda x: x.href == url and x.read).count():
        logger.debug(f'已經查詢過 {url}')
        return
    r = requests.get(url, headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8,zh-CN;q=0.7,en-US;q=0.6",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    })

    dom = pq(r.text)
    # create Word
    word_name = dom('span.hw.dhw').eq(0).text()
    if models.Word.select(lambda x: x.name == word_name):
        logger.warning(f'word name is already in db: {word_name}')
        return
    word = models.Word(
        name=word_name,
        part_of_speech=dom('span.dpos').eq(0).text(),
        sound=dom('.us span.ipa.lpr-2').eq(0).text(),
    )

    # create Explain
    for explain_el in dom('div.def-block').items():
        explain_en = explain_el('div.def').text()
        explain_ch = explain_el('.ddef_b > .break-cj').text()
        explain = models.Explain(
            word=word,
            en=explain_en,
            ch=explain_ch,
        )
        # create Sentence
        for sentence_el in explain_el('div.examp').items():
            sentence_en = sentence_el('span.eg').text()
            sentence_ch = sentence_el('span.trans.hdb').text()
            models.Sentence(
                explain=explain,
                en=sentence_en,
                ch=sentence_ch,
            )

    for word_el in dom('span > a.query').items():
        href = word_el.attr('href')
        count_ = not models.Url.select(lambda x: x.href == href).count()
        if count_:
            models.Url(
                href=href,
            )
            flush()

            logger.debug(f'new href: {href}')

    # update models.Url
    url_instance = models.Url.select(lambda x: x.href == url).first()
    if url_instance:
        url_instance.read = True
    else:
        models.Url(href=url, read=True)
    flush()
    logger.debug(f'新增結束 {url}')


@models.db_session
def crawl_new_words():
    """
    crawl 所有新的單字
    """
    urls = models.Url.select(lambda x: not x.read)
    for url in urls:
        crawl_word(url.href)


if __name__ == '__main__':
    logger.info(f'before Word count: {models.Word.select().count()}')
    crawl_word('persnickety')
    crawl_new_words()
    logger.info(f'Word count: {models.Word.select().count()}')
