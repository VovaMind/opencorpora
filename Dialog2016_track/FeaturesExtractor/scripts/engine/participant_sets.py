# -*- coding: utf-8 -*-

from participant_output import ParticipantOutput

import os

class ParticipantSets(object):
	'''Наборы данных от участников соревнований.'''
	def __init__(self, documents_list):
		self.documents_list = documents_list
	@staticmethod
	def answer_field(track_id):
		return "answer" + str(track_id) + "#"
	def participant_outputs(self, track_id):
		participant_info = {} # answer[id]#name -> (id, path)
		all_names = []
		for doc_info in self.documents_list.load():
			if not all_names:
				names = filter(lambda x: x.startswith(ParticipantSets.answer_field(track_id)), 
					doc_info.keys())
				all_names = list(names)
			for name in all_names:
				if name not in participant_info:
					participant_info[name] = []
				if not doc_info[name]:
					continue
				participant_info[name].append((doc_info["info#id"], doc_info[name]))
		for name in all_names:
			participant_name = name[len(ParticipantSets.answer_field(track_id)):]
			yield ParticipantOutput(participant_name, participant_info[name])
