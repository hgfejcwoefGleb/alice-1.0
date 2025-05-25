#ФУНКЦИЯ ДЛЯ НОВОСТЕЙ
from bs4 import BeautifulSoup
import urllib.request

def news_title(type_chose):   #когда скажет какую-нибудь из рубрик
    types_t = ['Postupaushim', 'Obrazovsnie', 'Nauka', 'Expertiza', 'Obshestvo', 'SvobodnoeObshenie', 'UniversitetZizn',
               'Prioritet2030', 'ProgRasv2030']
    types_tt = ['Поступающим', 'Образование', 'Наука', 'Экспертиза', 'Общество', 'Свободное общение', 'Университетская жизнь',
               'Приоритет 2030', 'Программа развития 2030']
    #type_chose = input() #(эта переменная дальше нужна для работы, сохраняем ее) тут будет одна из рубрик
    for i in range(len(types_t)):
        if types_t[i] == type_chose:
            type_chose_ = i + 1
            break
        elif type_chose == 'VseNovosti':
            type_chose_ = 10
            break
    if type_chose == 8:
        amount_news = 1
    elif type_chose == 9:
        amount_news = 2
    else:
        amount_news = 7

    html_page_news = urllib.request.urlopen("https://nnov.hse.ru/news/")
    soup = BeautifulSoup(html_page_news, "lxml")
    types_l = [] # переменная для ссылок на рубрики новостей

    for link in soup.find_all('a'):
        if link.get_text() in types_tt and len(types_l) < 9:
            href = link.get('href')

            types_l.append(href) #заполнили список ссылками на стр с разными рубриками новостей

    if type_chose_ < 10:
      html_page_news1 = urllib.request.urlopen(types_l[type_chose_ - 1])
      soup2 = BeautifulSoup(html_page_news1, "lxml")
    else:                  #создаем объект под опред страничку с новостями
      html_page_news1 = html_page_news
      soup2 = soup

    headings_l = [] #для заголовков ссылок на опред новость конкретной рубрики
    headings_t = [] #для заголовков названий опред новостей конкретной рубрики
    subs = [] #для краткого содержания новости
    for link in soup2.select('h2.first_child'):
        if len(headings_t) < amount_news:
            text = link.get_text()
            headings_t.append(text)  #заполнили названиями заголовков

    for link in soup2.find_all('a'):
        if link.get_text() in headings_t and len(headings_l) < amount_news:
            href = link.get('href')
            headings_l.append(href) #заполнили список ссылками на стр с конкретными новостей

    for link in soup2.select('div.post__text'):
        text = link.get_text()
        if text != '' and len(subs) < amount_news:
            subs.append(text)     #заполнили кратким содержанием выбранных новостей

    return headings_t, headings_l, subs, len(headings_t)
