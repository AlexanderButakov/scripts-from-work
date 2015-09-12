# -*- coding: utf-8 -*-

import re
import sys
import time

print	# отделить "Searching..." в командной строке

# кусрк формата rtf для вставки в готовый файл
start = r"{\rtf1\ansi\deff0{\fonttbl{\f0\fswiss\fprq2\fcharset0 Arial;}" + "\n" + r"{\f1\fswiss\fprq2\fcharset0 Arial;}{\f2\fswiss\fprq2\fcharset238{\*\fname Arial;}Arial CE;}}" + "\n" + r"{\colortbl ;\red128\green0\blue0;\red0\green0\blue0;\red0\green0\blue255;\red255\green0\blue0;\red0\green128\blue0;}" + "\n"
end = "}"

# строка для восстановления Difference # n
difference = "Difference #"

# Аргументы для командной строки: 0 - сам скрипт, 1 - файл rtf, 2 - искомое слово в new, 3 - искомое слово в old
diff_file = sys.argv[1]
new_item = sys.argv[2]
old_item = sys.argv[3]

# читаем rtf файл
file_open = open(diff_file,'r')
text = file_open.read()
file_open.close()

# разбиваем на строки по шаблону ('Difference #') и формируем список diffs
splitt = re.compile('Difference #')
diffs = splitt.split(text)

# маркеры конца выделения цветом
endpos_1 = re.compile(r"\\cf2")
endpos_2 = re.compile(r"\\cf0")

# список, в котором будут целевые разницы
matched_diffs = []

# для статистики
count_diffs = 0

# для отображения прогресса
j = 1

# Идем по списку diffs, берем отдельную разницу, ищем в ней перевод "T1:",
# и дальше ищем в подстроке от "T1:" до конца diff. Находим последовательность
# "\cf4" или \cf6, если это \cf6, то переписываем кусок формата для конечного rtf.
# В строке от "\cf4/6" вправо ищем "\cf2" или "\cf0", выделяем это в подстроку и
# сохраняем в новый список, где содержатся все выделенные красным цветом слова из 
# перевода T1. Теперь находим последовательность "\cf5". В строке справа от неё 
# ищем "\cf2" или "\cf0", выделяем это в подстроку и # сохраняем в новый список,
# где содержатся все выделенные зелёным цветом слова из перевода T2.
# Дальше ищем заданные слова в этих двух списках, если они там есть, то сохраняем
# всю diff в новый список matched_diffs

for diff in diffs:
	tagged_new = []
	tagged_old = []

	progress = j*100 / len(diffs)
	sys.stdout.write("\r" + "Searching... " + str(progress) + "%")
	sys.stdout.flush

	t_index = diff.find("T1:")

	sliced_diff = diff[t_index+2:]
		
	for i in range(len(sliced_diff)-1):

		if sliced_diff[i] == "\\" and sliced_diff[i+1] == "c" and (sliced_diff[i+3] == "4" or sliced_diff[i+3] == "6"):

			if sliced_diff[i+3] == "6":

				start = r"{\rtf1\ansi\deff0{\fonttbl{\f0\fnil\fcharset0 Arial;}{\f1\fnil\fcharset204{\*\fname Arial;}Arial CYR;}{\f2\fmodern\fprq1\fcharset129 Gulim;}{\f3\froman\fprq1\fcharset128 MS PGothic;}{\f4\fmodern\fprq6\fcharset134 SimSun;}}" + "\n" + r"{\colortbl ;\red0\green0\blue0;\red128\green0\blue0;\red136\green0\blue0;\red0\green0\blue255;\red0\green128\blue0;\red255\green0\blue0;}"
			
			if endpos_1.search(sliced_diff[i+4:]):
				match_1 = endpos_1.search(sliced_diff[i+4:])
				new_endpos = match_1.end()

			elif endpos_2.search(sliced_diff[i+4:]):
				match_1 = endpos_2.search(sliced_diff[i+4:])
				new_endpos = match_1.end()
			
			if len(tagged_new) == 0:
				tagged_new.append(sliced_diff[i+5:i+new_endpos])
				i = i + 1
			else:
				tagged_new.append(sliced_diff[i+5:i+new_endpos])
				i = i + 1

		if sliced_diff[i] == "\\" and sliced_diff[i+1] == "c" and sliced_diff[i+3] == "5":
			
			if endpos_1.search(sliced_diff[i+4:]):
				match_2 = endpos_1.search(sliced_diff[i+4:])
				new_endpos2 = match_2.end()

			elif endpos_2.search(sliced_diff[i+4:]):
				match_2 = endpos_2.search(sliced_diff[i+4:])
				new_endpos2 = match_2.end()
			
			if len(tagged_new) == 0:
				tagged_old.append(sliced_diff[i+5:i+new_endpos2])
				i = i + 1
			else:
				tagged_old.append(sliced_diff[i+5:i+new_endpos2])
				i = i + 1
	
	if new_item in " ".join(tagged_new).lower() and old_item in " ".join(tagged_old).lower():
		matched_diffs.append(difference + diff)
		count_diffs+=1

	j+=1

# быстрая часть, реализованная на регулярных выражениях. Работает в 4 раза быстрее,
# но является "жадной"

# false = []
# what = re.compile(r'\\cf4.*\\cf2')
# that = re.compile(r'\\cf5.*\\cf2')

# for item in diffs:
# 	if what.search(item) and that.search(item):
# 		m1 = what.search(item)
# 		m2 = that.search(item)
# 		if new_item in m1.group().lower() and old_item in m2.group().lower():
# 			matched_diffs.append("\par\cf1\\b\\" + item)
# 			count_diffs+=1
# 		else:
# 			false.append(item)

file_write = r"diff_" + new_item + "_" + old_item + ".rtf"
file_open_w = open(file_write, "w")
file_open_w.write(start)
file_open_w.write("Differences found: " + str(count_diffs) + "\t" + "New = " + new_item + ";" + " " + "Old = " + old_item + "\n" + "\cf2\\fs16" + "\n" + "\par\\fs16" + "\n" + "\par\cf1\\b\\" + "\n")
for t in matched_diffs:
	file_open_w.write("".join(t))
file_open_w.write("\n" + end)
file_open_w.close()