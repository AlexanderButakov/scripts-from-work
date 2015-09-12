# -*- coding: utf-8 -*-
import urllib2
import sys
from datetime import date

"""
Скрипт скачивает указанные страницы и их количество 
с сайта mediametrics.ru, формирует список новостных заголовков,
собранных с этих страниц.
Запускать скрипт можно с разными параметрами, в зависимости от этого
будут скачиваться заголовки по разным тематикам: бизнес, спорт, IT,
Великобритания, США и пр.

"""


# get date for filenames
today = date.today()
d = today.strftime("%Y_%m_%d")

#sys arguments
option = sys.argv[1] 

def download_html():
    
    HTML_NAME = "http://mediametrics.ru/rating/"

    # если не заданы параметры при запуске, использовать эту страницу
    DEFAULT_NAME = "http://mediametrics.ru/rating/ru/day.html"
    pages = 3
    titles_join = ""
    index_p = 1
    global option

    # в зависимости от указанного параметра value будет прикрепляться к HTML_NAME
    options = {'--day':'ru/day.html','--tech':'hitech/ru/day.html','--sport':'sport/ru/day.html',
                '--biz':'business/ru/day.html','--gb':'gb/day.html','--us':'us/month.html'
                }

    for key, value in options.iteritems():

        if option == key:

            HTML_NAME = HTML_NAME + value

    while pages > 0:
    	
        html_temp = ""
        titles_raw = ""
        
        load_source = urllib2.urlopen(HTML_NAME + "?page=" + str(index_p))
        html_temp = load_source.read()
        start_titles = html_temp.find('tsv = "')
        end_titles = html_temp.find(r'\n";')
        titles_raw = html_temp[start_titles+13:end_titles]
        titles_join = titles_join + titles_raw
        
        pages = pages - 1
        index_p = index_p + 1

    return titles_join

# вместо функции лучше использовать HTMLParser().unescape()
def convert_entityrefs(string):

    html_chars = {
            '&raquo;':'»','&laquo;':'«','&nbsp;':' ','&ndash;':'–',
            '&quot;':'"','&prime;':'′','&Prime;':'″','&lsquo;':'‘',
            '&rsquo;':'’','&mdash;':'—','&sbquo;':'‚','&ldquo;':'“',
            '&rdquo;':'”','&bdquo;':'„','&euro;':'€','&pound;':'£',
            '&thinsp;':' ','&hellip;':'...','&shy;':'',"&#39;":"'",
            '&amp;':'&'
            }

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
                for key, value in html_chars.iteritems():
                    if tag == key:
                        tag = value
                        char_converted[s:i+1] = tag
                        flag = True
            else:
                for key, value in html_chars.iteritems():
                    if tag == key:
                        tag = value
                        char_converted[lst_s:lst_i+1] = tag
                        
    text_converted = ''.join(char_converted)

    return text_converted

# составляется список заголовков
def split_titles(titles):
	
	list_of_titles = []
	s = 0
	for i in range(len(titles)):

		if titles[i] == '\\' and titles[i+1] == 'n':
			if len(list_of_titles) > 0:
				list_of_titles.append(titles[s:i])
				s = i+2

			else:
				list_of_titles.append(titles[:i])
				s = i + 2
		elif i == len(titles) - 1:
			list_of_titles.append(titles[s:])

	return list_of_titles

# строки заголовков чистятся от лишей информации, 
# чтобы остался только текст
def get_clean_titles(lst):

	titles_grouped = []

	for item in lst:
	    titles_clean = []
	    tab_count = 0
	    s = 0
	    for i in range(len(item)-1):
	    	if item[i] == '	':
		        tab_count += 1
		        if len(titles_clean) > 0:
		        	titles_clean.append([item[s:i]])
		        	s = i + 1

		        else:
		        	titles_clean.append([item[:i]])
		        	s = i + 1
                if tab_count == 3:
                    titles_grouped.append(titles_clean)
                    break
	
	return titles_grouped

def main():
    
    global option

    titles_join = download_html()
    converted_entities = convert_entityrefs(titles_join)
    list_of_titles = split_titles(converted_entities)
    titles_clean = get_clean_titles(list_of_titles)

    prefixes = {'--day':'general_','--tech':'hitech_','--sport':'sport_',
                '--biz':'business_','--gb':'britain_','--us':'USA_'
                }

    for key, value in prefixes.iteritems():

        if option == key:

            prefix = value

    filename = prefix + r"news_titles" +"_" + d + ".txt"
    file_w = open(filename,'w')
    for title in titles_clean:
    	file_w.write(''.join(title[1]) + '\n')


if __name__ == '__main__':
    main()
