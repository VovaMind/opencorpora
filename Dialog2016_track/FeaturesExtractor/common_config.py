# -*- coding: utf-8 -*-
''' main-файл для извлечения признаков '''

WORD2VEC_FEATURES_COUNT = 1000

# Путь к бинарникам (в нашем случае mystem)
BINARY_PATH = "..\\bin"
MYSTEM_FILE_NAME = "mystem.exe"
OUTPUT_DIR = "..."
FACTRUEVAL_DIR = ".../factRuEval-2016/"
WORDTOVEC_DIR = "..."
INPUT_DIR = ".../input/"

# Парметры для get_corpora_features.py
GET_CORPORA_FEATURES_PARAMS = {
	# Пишем результаты извлечения признаков для документов в эту папку
	"output_dir": OUTPUT_DIR + "parts/",
	# Папка с исходными текстами документов и их разбиением на токены
	"input_dir": FACTRUEVAL_DIR + "ctrlset/",
	# Папка внутри которой содержится набор подпапок с именами участников. 
	# Например, там должны быть подпапки "aquamarine_0", "pink_3.test", "violet_1.dev"
	"participants_dir": INPUT_DIR,
	# файл с w2v моделью
	"w2v_model_file": WORDTOVEC_DIR + "news.model.bin",
	# Сериализованный набор множеств для участников. 
	# Он строится в процессе обработки размеченного корпуса.
        "sets_dump_file": OUTPUT_DIR + "sets_dump.bin",
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
	"input_dir": GET_CORPORA_FEATURES_PARAMS["input_dir"],
	# Папка в которой находятся признаки. В нее же пишем итоговую разметку.
	"work_dir": GET_CORPORA_FEATURES_PARAMS["output_dir"] 
}

# Параметры для get_testset_features.py
GET_TESTSET_FEATURES_PARAMS = {
	# файл с w2v моделью
	"w2v_model_file": GET_CORPORA_FEATURES_PARAMS["w2v_model_file"],
	# Путь к папке с разметкой testset'а.
	"markup_dir": (FACTRUEVAL_DIR + "testset.half"),
	# Папка внутри которой содержится набор подпапок с именами участников. 
	# Например, там должны быть подпапки "aquamarine_0", "pink_3.test", "violet_1.dev"
	"participants_dir": GET_CORPORA_FEATURES_PARAMS["participants_dir"],
	# Путь к результирующему csv-файлу с данными.
	"output_file_name": OUTPUT_DIR + "MarkupData.csv",
	# Сериализованный набор множеств для участников. 
	# Он строится в процессе обработки размеченного корпуса.
	"sets_dump_file": GET_CORPORA_FEATURES_PARAMS["sets_dump_file"]
}

# Параметры для get_contest_format.py
GET_CONTEST_FORMAT_PARAMS = {
	# Пишем результаты извлечения признаков для документов в эту папку
	"work_dir": r"C:\development\OpenCorpora\FactExtAutoAssesst\data\!test_output",
}

# Парметры для get_span_keywords.py
GET_SPAN_KEYWORDS = {
	# Путь к размеченному корпусу.
	"markup_dir": FACTRUEVAL_DIR + "devset",
	# Результирующий каталог, в котором лежат списки слов, разделенные по файлам.
	"output_dir" : OUTPUT_DIR + "word_sets"
}
