# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import codecs, re, itertools

"""
Скрипт вытаскивает из текстовых файлов, указанных в dir_file, 
одно-, двух-, трехсловные названия в кавычках по regexp'у и предложения,
в которых они были найдены. Сравнивает со списком организаций и списком окончаний,
отбрасывает совпавшие. 
Два вспомогательных класса (LoadExternalLists и TextSegmentor) нужны
для разбивки русского текста на предложения.

# stopwords - содержит список стоп-слов.
# titled_stopwords - содержит список стоп-слов с повышенной первой бувой (необходим для разбиения на предложения)
# abbreviations - соержит список сокращений с точкой, после которых не разбивать на предложения.
"""

class LoadExternalLists(object):
    
    """
    Загружаем в память файл стоп-слов (+ с ББ) и файл сокращений для сплиттера
    """

    def __init__(self):

        self.stopwords = set()
        self.titled_stopwords = set()
        self.abbreviations = set()
        self.organizations = set()
        self.correct = []
                        
        
    def loadStopWords(self):

        file_openstopw = codecs.open(r".\txt_resources\stopwords_ru.txt",'r','utf-16')
        self.stopwords = set(file_openstopw.read().split('\r\n'))
        file_openstopw.close()

        return self.stopwords

    def loadTitledStopwords(self):
        
        self.titled_stopwords = set([word.title() for word in self.loadStopWords()])

        return self.titled_stopwords

    def loadAbbreviations(self):

        file_openabbrev = codecs.open(r'.\txt_resources\abbrevs_ru.txt','r', 'utf-16')
        self.abbreviations = set(file_openabbrev.read().split('\r\n'))
        file_openabbrev.close()

        return self.abbreviations

    def loadOrganizations(self):

        with codecs.open(r'.\txt_resources\organizations_geo.txt', 'r', 'utf-16') as infile:
            lst_organizations = infile.read().split('\r\n')
            self.organizations = set([word.lower() for word in lst_organizations])

        return self.organizations

    def loadCorrect(self):

        with codecs.open(r'.\txt_resources\org_endings', 'r', 'utf-16') as infile:
            lst_correct = infile.read().split('\r\n')
            self.correct = tuple([word.lower() for word in lst_correct])

        return self.correct



class TextSegmentor(object):

    def __init__(self, titled_stopwords, ABBREVIATIONS):
        
        self.titled_stopwords = titled_stopwords
        self.ABBREVIATIONS = ABBREVIATIONS

    def splitToParagraphs(self, text):

        """
        Функция разбивает текст на абзацы по новой строке (\n)
        """
        paragraphs = []
        paragraphs = re.split(r'[\r\n]+', text)
        

        return paragraphs

    
    def splitToSents(self, paragraphs):
        """
        Первичное разбиение на предложения. Функция принимает на вход
        список абзацев, возвращает список с вложенными списками предложений.
        """

        terminators = ['.', '!', '?', ':', ';', '…']    # знаки конца предложения
        re_terminators = re.compile(r'[\.\!\?\:\;\…]')    # для быстрого определения, есть ли знаки в абзаце
        set_of_sentences = []
        
        punctuation = "!\"#£$¥%&'()*+±×÷,-./:;<=>?¿@[\]^ˆ¨_—`–{|}~≈→↓’“”«»‘…¦′″§¼⅜½¾⅘©•"    # знаки для обрезания вокруг слов
        
        punctsplit = re.compile(r'[\s\(\"\'\’\“\”\«\»\‘\[\{\<~…` �⌂\;\:\—\′\″ ]+')        # знаки, по которым разбивать на слова

                                    # Для rightcontext: если после терминатора стоит: 1) несколько пробелов или 
                                    # 2) знак в [], повторяющийся один или несколько раз,
                                    # + [несколько пробелов или знак препинания без пробела
                                    # или 3) конструкция типа .[1]
                                    # И дальше ББ или один из знаков или цифра
        rightcontext = re.compile(r'( +|[\"\'\’\“\”\«\»\‘\)\]\}\>\`\′\″]+[\s\.\!\?]+|\[ *[a-zA-Zа-яА-Я0-9,\.\-\:]+ *\]+\s+)[A-ZА-Я\d\"\'\’\“\«\‘\(\[\<\{\`\′\″]')
        
                                    # если левый от терминатора контекст(слово) = ББ(опционно) + слово с _ или \'
        leftcontext_2 = re.compile(r'[A-ZА-Я]?[a-zа-я_\']+')
        
                                    # если правый от терминатора контекст(слово) = (опционно скобка или кавычка)+
                                    # ББ + слово(опционно)
        rightcontext_2 = re.compile(r'[\"\“\«\‘\(\[\<\{\`]?[A-ZА-Я]([A-ZА-Яa-zа-я\.\']+)?')
        
        new_sent = re.compile(r'\s+[\(\[\<\{]')
        
        for paragraph in paragraphs:

            begin = 0
            start = 0
            sentences = []

            num_of_sents = 0
            
            paragraph = paragraph.strip()                                   # удаление висячих знаков в конце и начале абзаца

            if not re_terminators.search(paragraph):                        # проверка, если нет знаков препинания --> скинуть в список
                sentences.append(paragraph[start:])
            
            else:

                all_terminators = re_terminators.finditer(paragraph)            # список всех терминаторов абзаца

                for terminator in all_terminators:

                    i = terminator.start()                                        # начальная позиция re-объекта - это индекс в абзаце

                    if rightcontext.match(paragraph[i+1:]):                        # если совпадает контекст справа от терминатора, запоминаем его
                        match = rightcontext.match(paragraph[i+1:])

                        if paragraph[i] == '.':
                                
                            s = punctsplit.split(paragraph[start:i])

                            if s[len(s)-1] not in self.ABBREVIATIONS:                        # если последнее слово слева от точки не аббревиатура, складываем
                                sentences.append(paragraph[start:i+(match.end()-1)])
                                start = i + match.end()
                            
                            else:
                                
                                if new_sent.match(paragraph[i+1:]):
                                    sentences.append(paragraph[start:i+(match.end()-1)])
                                    start = i + match.end()

                                # если слева слово из аббрев. (H.), а справа стоп-слово с ББ, складываем предложение
                                elif punctsplit.split(paragraph[i+2:])[0].strip(punctuation) in self.titled_stopwords:
                                    sentences.append(paragraph[start:i+1])
                                    start = i + 1
                        else:
                            sentences.append(paragraph[start:i+(match.end()-1)])
                            start = i + match.end()

                    # обработка случаев, когда между предложениями пропущен пробел. (.. in it.The...)
                    else:

                        k = punctsplit.split(paragraph[start:i])
                        lastword = len(k[len(k)-1])

                        if leftcontext_2.match(paragraph[i-lastword:i]) and rightcontext_2.match(paragraph[i+1:]):
                            match = rightcontext_2.match(paragraph[i+1:])
                                
                            if paragraph[i] == '.':
                                                                   
                                if k[len(k)-1] not in self.ABBREVIATIONS:
                                    sentences.append(paragraph[start:i+1])
                                    start = i + 1
                            else:
                                sentences.append(paragraph[start:i+1])
                                start = i + 1
            
                sentences.append(paragraph[start:])

            set_of_sentences.append(sentences)

        return set_of_sentences


    def segment(self,text):
        """
        Функция вызывает последовательно две функции: 
        1) разбивка на абзацы
        2) разбивка на предложения, 
        
        Возвращает список вида [[[],[]],[[],[]],[[]]].
        Вторая вложенность - абзацы, внутренние списки - предложения.
        """

        paragraphs = self.splitToParagraphs(text)
        set_of_sentences = self.splitToSents(paragraphs)
                
        return set_of_sentences


def main():

    external_lst = LoadExternalLists()
    STOPWORDS = external_lst.loadStopWords()
    TITLED_STOPWORDS = external_lst.loadTitledStopwords()
    ABBREVIATIONS = external_lst.loadAbbreviations()
    ORGANIZATIONS = external_lst.loadOrganizations()
    CORRECT = external_lst.loadCorrect()
    punctuation = "!\"#£$¥%&'()*+±×÷,-./:;<=>?¿@[\]^ˆ¨_—`–{|}~≈→↓’“”«»‘…¦′″§¼⅜½¾⅘©•"
    
    
    large_quotes_list = []
    docs_found = 0
    docs_read = 0
    sents_found = 0

    listdir = r'V:\Linguistic Department\TestTrackData\RE_2016\10497\textbase.dir'

    with codecs.open(listdir, 'r', 'utf-16') as infile:
            dir_file = infile.read()

    for filename in dir_file.split('\n'):
        
        filename = filename.strip()
        print filename
        
        try:
            with codecs.open(filename, 'r', 'utf-16') as infile:
                TEXT = infile.read()
                docs_read+=1
        except (UnicodeDecodeError, UnicodeError, IOError):
            pass
        

        textsegm_object = TextSegmentor(TITLED_STOPWORDS, ABBREVIATIONS)
        LIST_OF_SENTENCES = textsegm_object.segment(TEXT)
        ALLSENTENCES = list(itertools.chain.from_iterable(LIST_OF_SENTENCES))

        quotes_pattern = re.compile(r'[\"\“\«\‘\′\″][А-Я][^\"\“\«\‘\′\″\”\»\’\.\,\?\!\№\%°¶Ѓї•]+[\"\′\″\”\»\’]')
        all_quotes = {}

        for sentence in ALLSENTENCES:
            proper_quotes = []
            quotes_list = quotes_pattern.findall(sentence)
            if len(quotes_list) > 0:
                for quote in quotes_list:
                    if len(quote.split(' ')) <= 3:
                        if quote.strip(punctuation).lower() not in ORGANIZATIONS and not quote.strip(punctuation).endswith(CORRECT):
                        # if quote.strip(punctuation).lower() in ORGANIZATIONS and not quote.strip(punctuation).lower().endswith(CORRECT):    # для организаций из словаря
                            proper_quotes.append(quote)

                if len(proper_quotes) > 0:
                    all_quotes[sentence] = proper_quotes
                    sents_found+=1
                
        if len(all_quotes) > 0:
            if all_quotes not in large_quotes_list:
                large_quotes_list.append(all_quotes)
                docs_found+=1


    print docs_found
    print docs_read
    print sents_found

    with codecs.open(r'organizations_from_GenDict.txt', 'w', 'utf-16') as outfile:
        for dct in large_quotes_list:
            for key, value in dct.iteritems():
                outfile.write(key)
                outfile.write('\t')
                outfile.write('['+', '.join(value)+']')
                outfile.write('\n\n')



if __name__ == '__main__':
    main()