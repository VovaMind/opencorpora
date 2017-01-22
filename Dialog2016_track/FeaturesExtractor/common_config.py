# -*- coding: utf-8 -*-
''' main-файл для извлечения признаков '''

WORD2VEC_FEATURES_COUNT = 1000

# Путь к бинарникам (в нашем случае mystem)
BINARY_PATH = "..\\bin"
MYSTEM_FILE_NAME = "mystem.exe"

# Парметры для get_corpora_features.py
GET_CORPORA_FEATURES_PARAMS = {
	# Пишем результаты извлечения признаков для документов в эту папку
	"output_dir": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\!test_output",
	# Папка с исходными текстами документов и их разбиением на токены
	"input_dir": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\!bocharov\tokenizedset",
	# Папка внутри которой содержится набор подпапок с именами участников. 
	# Например, там должны быть подпапки "aquamarine_0", "pink_3.test", "violet_1.dev"
	"participants_dir": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\factrueval2016",
	# файл с w2v моделью
	"w2v_model_file": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\news_win20.model.bin",
	# Сериализованный набор множеств для участников. 
	# Он строится в процессе обработки размеченного корпуса.
	"sets_dump_file": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\sets_dump.bin",
	# Количество частей на которые делим весь корпус для параллельного извлечения признаков
	"parts_count": 10
}

# Признаки для токенов занимают много простанства на диске.
# Поэтому делим весь корпус на куски по 100 документов.
# В этом случае размер одного файла с признаками получается около 1гб.
DOCUMENTS_CHUNK_SIZE = 100

# Параметры для markup_builder.py
MARKUP_BUILDER_PARAMS = {
	# Папка с исходными текстами документов и их разбиением на токены
	"input_dir": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\!bocharov\tokenizedset",
	# Папка в которой находятся признаки. В нее же пишем итоговую разметку.
	"work_dir": r'C:\development\OpenCorpora\FactExtAutoAssesst\data\!test_output'
}

# Параметры для get_testset_features.py
GET_TESTSET_FEATURES_PARAMS = {
	# файл с w2v моделью
	"w2v_model_file": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\news_win20.model.bin",
	# Путь к папке с разметкой testset'а.
	"markup_dir": (r"C:\development\OpenCorpora\FactExtAutoAssesst\data"
				r"\factRuEval-2016-master\factRuEval-2016-master\testset"),
	# Папка внутри которой содержится набор подпапок с именами участников. 
	# Например, там должны быть подпапки "aquamarine_0", "pink_3.test", "violet_1.dev"
	"participants_dir": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\factrueval2016",
	# Путь к результирующему csv-файлу с данными.
	"output_file_name": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\MarkupData.csv",
	# Сериализованный набор множеств для участников. 
	# Он строится в процессе обработки размеченного корпуса.
	"sets_dump_file": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\sets_dump.bin"
}

# Параметры для get_contest_format.py
GET_CONTEST_FORMAT_PARAMS = {
	# Пишем результаты извлечения признаков для документов в эту папку
	"work_dir": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\!test_output",
}

# Парметры для get_span_keywords.py
GET_SPAN_KEYWORDS = {
	# Путь к размеченному корпусу.
	"markup_dir": r"C:\development\OpenCorpora\FactExtAutoAssesst\data"
				r"\factRuEval-2016-master\factRuEval-2016-master\devset",
	# Результирующий каталог, в котором лежат списки слов, разделенные по файлам.
	"output_dir" : r"C:\development\OpenCorpora\FactExtAutoAssesst\data\word_sets"
}
