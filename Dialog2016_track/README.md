# Введение

Хотим разметить корпус онто-объектами. 

Данные берем из результатов соренования, проходившего в рамках конференции Диалог 2016.

Участники дали результаты для размеченных корпусов (тренировочного и тестовго) и для общего корпуса.

Нужно разметить общий корпус (https://www.dropbox.com/s/fja8gzpf59hfu1p/testset-v2.zip?dl=0), обучив композицию решений участников на размеченном корпусе.

Подробности о разметке: http://opencorpora.org/wiki/Nermanual/2

Размеченный корпус: https://github.com/dialogue-evaluation/factRuEval-2016

# Настройка

Настройка перед запуском:
1. Для извлечения признаков используется Python 3.4. Нужно установить пакеты: gensim, pandas, pytest.
2. Для построения моделей и ответов используется R. Нужно установить пакеты: class, randomForest, adabag.
3. Перед запуском нужно скачать [w2v модель](http://rusvectores.org/static/models/rusvectores2/news_rusvectores2.bin.gz) (скопировать в FeaturesExtractor/scripts/engine/data) и [mystem](https://tech.yandex.ru/mystem/) (скопировать в FeaturesExtractor/scripts/engine/bin).
4. Нужно проверить, что тесты проходят. Для этого нужно перейти в FeaturesExtractor/test и запустить "python -m pytest". Должно пройти 16 тестов. 

ВАЖНО! В тестах предполагается, что w2v файл называется "news_win20.model.bin", а испольняемый файл для mystem называется "mystem.exe". В случае необходимости нужно заменить эти названия в тестах (py-файлы) и в конфигах (json-файлы).

# Основной pipeline для получения разметки

## Списки документов

Различные корпуса описываются с помощью csv-файлов. Имена стоблцов в csv-файле:

Имя стоблца | Описание
--- | ---
info#id | Id документа. По ним происходит разделение корпуса на части.
info#text | Путь к тексту документа.
info#contest_tokenization | Путь к токенизации в формате соревнования (tokens-файл) для документа.
info#tokenization | Путь к "обычной" токенизации (токены идут по одному в строке) для документа.
info#spans | Путь к файлу с описанием спанов (spans-файл) для документа.
info#objects | Путь к файлу с описание объектов (objects-файл) для документа.
answer1#имя\_участника | Путь к файлу с ответом участника с именем "имя\_участника" для докумета.

ВАЖНО! все пути задаются относительно базовой директории (см. следующий раздел).

Примеры csv-файлов можно посмотреть в FeaturesExtractor/tests.

## Конфиги

Каждый запуск python-скрипта предполагает задание json-конфига. Конфиги используют следующие имена:

Имя в конфиге | Описание
--- | ---
devset_documents_list | Путь к csv-файлу, который описывает файлы devset'а.
devset_base_dir | Базовая директория для путей к файлам из devset_documents_list.
words_set_dir | Каталог в котором лежат газетиры. Каждый газетир - это файл со списком слов. Мы извлекаем для каждого слова и каждого газетира бинарный признак принадлежности слова газетиру.
testset_documents_list | Путь к csv-файлу, который описывает файлы testset'а.
testset_base_dir | Базовая директория для путей к файлам из testset_documents_list.
w2v_file_name | Имя файла с w2v моделью.
mystem_file_name | Имя исполняемого файла для mystem.
testset_features_file | Путь к csv-файлу с признаками для testset'а. Этот файл нужно для построения модели.
sets_collection_file | Путь к промежуточному файлу. Он создается скриптом get\_testset\_features.py и используется скриптом get\_corpora\_features.py.
corpora_documents_list | Путь к csv-файлу, который описывает большой неразмеченный корпус.
corpora_base_dir | Базовая директория для путей к файлам из corpora_documents_list.
corpora_chunk_size | Сколько документов класть в один csv-файл. По-умолчанию 100.
corpora_parts_count | На сколько частей разбиваем корпус для параллельных вычислений. По-умолчанию 10.
output_dir | Директория в которую складываем все промежуточные результаты и ответы.

Больше деталей можно узнать по коду в FeaturesExtractor/tests и в FeaturesExtractor/scripts.

## Схема запуска

* Подготвка словарей по devset. Мы извлекаем частотные слова для определенного типа спанов. Запуск:
```bash
python FeaturesExtractor/scripts/get_span_keywords.py config_file
```
Это нужно проделать только один раз. Важно извлекать данные из devset'а, чтобы избежать перееобучения на testset'е. Остальные газетиры нужно складывать в ту же директорию (words_set_dir в конфиге).
* Извлечение признаков для testset'а или его части. Запуск:
```bash
python FeaturesExtractor/scripts/get_testset_features.py config_file
```
* Построение модели. Запуск:
```bash
Rscript DataAnalysis/token_objects.R
Rscript DataAnalysis/token_span_types.R
```
* Извлечение признаков из всего корпуса. Запуск:
```bash
python FeaturesExtractor/scripts/get_corpora_features.py config_file part_id
```
Предполагается параллельный запуск нескольких скриптоа с part_id от 0 до corpora_parts_count (задается в конфиге) - 1
* Получение объекты и спаны для всего корпуса. Запуск:
```bash
Rscript DataAnalysis/restore_full_corpus.R input_dir
```
Предполагается параллельный запуск скрипта для каждой из частей. Нужно указывать имена конечных директорий в которых лежат файлы \_features\_\*.csv.
* Построение итоговой разметки. Запуск:
```bash
python FeaturesExtractor/scripts/markup_builder.py config_file part_id
```
Предполагается параллельный запуск нескольких скриптоа с part_id от 0 до corpora_parts_count (задается в конфиге) - 1 для построения результата для конкретной части.
