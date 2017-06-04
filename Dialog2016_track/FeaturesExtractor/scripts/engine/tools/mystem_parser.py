# -*- coding: utf-8 -*-
''' Парсер результатов mystem'а '''

import re

# Source: https://tech.yandex.ru/mystem/doc/grammemes-values-docpage/
GRAMMEME_TO_FEATURE = {
	# Время глагола
	"наст": ("verb_time", "nast"),
	"непрош": ("verb_time", "neprosh"),
	"прош": ("verb_time", "prosh"),
	# Падеж
	"им": ("case", "im"),
	"род": ("case", "rod"),
	"дат": ("case", "dat"),
	"вин": ("case", "vin"),
	"твор": ("case", "tvor"),
	"пр": ("case", "pr"),
	"парт": ("case", "part"),
	"местн": ("case", "mestn"),
	"зват": ("case", "zvat"),
	# Число
	"ед": ("number", "single"),
	"мн": ("number", "plural"),
	# Репрезентация и наклонение глагола
	"деепр": ("verb_inclination", "ger"),
	"инф": ("verb_inclination", "inf"),
	"прич": ("verb_inclination", "partcp"),
	"изъяв": ("verb_inclination", "indic"),
	"пов": ("verb_inclination", "imper"),
	# Форма прилагательных
	"кр": ("adv_form", "brev"),
	"полн": ("adv_form", "plen"),
	"притяж": ("adv_form", "poss"),
	# Степень сравнения
	"прев": ("comparision_level", "supr"),
	"срав": ("comparision_level", "comp"),
	# Лицо глагола
	"1-л": ("verb_person", "1p"),
	"2-л": ("verb_person", "2p"),
	"3-л": ("verb_person", "3p"),
	# Род
	"муж": ("genious", "g_m"),
	"жен": ("genious", "g_f"),
	"сред": ("genious", "f_n"),
	# Вид
	"несов": ("kind", "ipf"),
	"сов": ("kind", "pf"),
	# Залог
	"действ": ("voice", "act"),
	"страд": ("voice", "pass"),
	# Одушевленность
	"од": ("animations", "anim"),
	"неод": ("animations", "inan"),
	# Переходность
	"пе": ("transitive", "tran"),
	"нп": ("transitive", "intr"),
}

class MystemParser(object):
	def __init__(self):
		self.features_list = set(map(lambda x: x[0], GRAMMEME_TO_FEATURE.values()))
	def parse(self, mystem_str):
		result = {}
		for feature in self.features_list:
			result[feature] = "undefined"
		for grammeme in re.split(",|=", mystem_str.lower()):
			if grammeme not in GRAMMEME_TO_FEATURE:
				continue
			result[GRAMMEME_TO_FEATURE[grammeme][0]] = GRAMMEME_TO_FEATURE[grammeme][1]
		return result
