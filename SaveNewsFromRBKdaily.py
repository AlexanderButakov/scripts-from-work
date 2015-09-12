# -*- coding: utf-8 -*-

# Скрипт запрашивает у пользователя ссылку с сайта rbkdaily.ru,
# скачивает html-код страницы, чистит от тегов, конвертирует html-мнемоники и
# оставляет только заголовок, текст статьи и ссылку



import urllib2
import re
from datetime import date
import os
import sys

#### получаем дату ####

# для использования в имени файла
today = date.today()
d = today.strftime("%m_%d")

#### скачиваем содержимое страницы ####
print # для красоты вывода в консоль

get_link = raw_input("Enter a web-link to an article from rbkdaily.ru: ")


def get_article(string):

    """
    Функция скачивает html-код страницы методом urllib2.urlopen.
    В коде выделяется определённая часть от тега 'tag_begin' до 
    тега 'tag_end'. В этом куске ('article') ищутся html-теги
    по регулярному выражению ('html_tag_regex') и удаляются. Здесь
    же ищется название статьи. Функция возвращает чистый текст статьи
    ('article_clean') и заголовок ('title').

    """

    html_source = urllib2.urlopen(string)
    full_text = str(html_source.read())
    
    tag_begin = full_text.find('<div class="b-article-item-body__text-text">')
    tag_end = full_text.find('<div class="b-tags">')

    article = full_text[tag_begin:tag_end]

    html_tag_regex = re.compile(r'<[^<]+>')
    article_clean = html_tag_regex.sub('', article)

    titel_regex = re.search(r'<h2.*>(.*)</h2>', full_text)
    title = '\t' + titel_regex.group(1)
    

    return article_clean, title

#### преобразуем html-символы ####
# вместо функции лучше использовать HTMLParser().unescape()
def convert_html_symbol(string):

    """
    Функция ищет в очищенном от тегов тексте html-мнемоники (&nbsp;)
    и заменяет их, следуя списку html_char. 
    Первый if: В строке находится индекс символа '&', запоминается 
    и скидывается в список 'char_converted', где уже находятся 
    неудовлетворившие условию симолы. Здесь же запоминается индекс
    символа '&' в новом списке (lst_s).
    Второй if: Если символ = ';', то выделяется подстрока от '&' до
    ';' (tag), ограничивая мнемонику. Здесь же запоминается индекс 
    ';' в новом списке (lst_i). 
    Если флаг выключен ('flag == False'), значит замены ещё не было,
    и номера индексов идентичны номерам в строке, список не укоротился.
    Если tag находится в списке 'html_char', то он заменятеся на 
    соответствующий ему символ. В списке место мнемоники занимает
    символ, список становится короче строки, включается флаг.
    Если флаг включен, мнемоники в списке заменяются по индексам lst_s
    и lst_i. 
    Функция возвращает строку, восстановленную из списка.

    """

    html_char = [
            ['&raquo;','»'],['&laquo;','«'],['&nbsp;',' '],['&ndash;','–'],
            ['&quot;','"'],['&prime;','′'],['&Prime;','″'],['&lsquo;','‘'],
            ['&rsquo;','’'],['&mdash;','—'],['&sbquo;','‚'],['&ldquo;','“'],
            ['&rdquo;','”'],['&bdquo;','„'],['&euro;','€'],['&pound;','£'],
            ['&thinsp;',' '],['&hellip;','...'],['&shy;',''],["&#39;","'"],
            ['&amp;','&']
            ]

    flag = False
    char_converted = []
    s = 0
    lst_s = 0
    lst_i = 0

    for i in range(len(string)):
            
        if string[i] == '&':
            s = i
            char_converted.append(string[i])
            lst_s = len(char_converted)-1   #индекс в листе для &
        else:
            char_converted.append(string[i]) 

        if string[i] == ';':
            tag = string[s:i+1]
            lst_i = len(char_converted)-1   # индекс в листе для ;
            
            if flag == False:
                for j in range(len(html_char)):
                    if tag == html_char[j][0]:
                        tag = html_char[j][1]
                        char_converted[s:i+1] = tag
                        flag = True
            else:
                for j in range(len(html_char)):
                    if tag == html_char[j][0]:
                        tag = html_char[j][1]
                        char_converted[lst_s:lst_i+1] = tag
                        
    text_converted = ''.join(char_converted)

    return text_converted

#### создаем файл формата "rbk_сегодняшняя_дата.txt" и сохраняем его ####
def file_save(text, title, link):

    """

    Функция сохраняет текстовый файл с текущей датой в названии,
    проверяет существует ли файл. Если существует, сохраняет
    следующий с приставкой _f, где f - цифра, начиная с "2".

    """

    global today
    global d
    global get_link
    filename = r"V:\Linguistic Department\TestTrackData\RE_2015\9578\Texts\txt\2015\rbk_" + d + ".txt"
    f = 2
    
    if os.path.exists(r"V:\Linguistic Department\TestTrackData\RE_2015\9578\Texts\txt\2015\rbk_" + d + "_" + str(f) + ".txt"):
	  	
		f = f + 1
		filename = r"V:\Linguistic Department\TestTrackData\RE_2015\9578\Texts\txt\2015\rbk_" + d + "_" + str(f) + ".txt"
		with open(filename,'w') as file_w: 
			file_w.write(title)
			file_w.write(text)
			file_w.write(link)
    
    elif os.path.exists(filename):
		filename = r"V:\Linguistic Department\TestTrackData\RE_2015\9578\Texts\txt\2015\rbk_" + d + "_" + str(f) + ".txt"
		with open(filename,'w') as file_w:
			file_w.write(title)
			file_w.write(text)
			file_w.write(link)	
    else:
    	with open(filename, 'w') as file_w:
            file_w.write(title)
            file_w.write(text)
            file_w.write(link)

#### вызываем функции ####
def main():

    article_clean, title = get_article(get_link)
    text_converted = convert_html_symbol(article_clean)
    file_save(text_converted, title, get_link)

main()

print

"""
Ниже скрипт спрашивает о желании сохранить больше одной статьи.
Интеракция происходит до тех пор, пока не будет введена 'N'.
"""

response = raw_input("Do you want to download another article? (Y/N) ")

while response == "Y":
    print
    get_link = raw_input("Enter a new web-link: ")
    print
    main()
    response = raw_input("Do you want to download another article? (Y/N) ")

else:
    print
    print "You will find your articles here: "
    sys.exit()