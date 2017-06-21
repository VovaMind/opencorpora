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

# Основной pipeline для получения разметки:

## Списки документов

TBD

## Конфиги

Каждый запуск python-скрипта предполагает задание json-конфига. Конфиги используют следующие имена:

Имя в конфиге | Описание
--- | ---
devset_documents_list | TBD
devset_base_dir | TBD
words_set_dir | TBD
testset_documents_list | TBD
testset_base_dir | TBD
w2v_file_name | TBD
mystem_file_name | TBD
testset_features_file | TBD
sets_collection_file | TBD
corpora_documents_list | TBD
corpora_base_dir | TBD
corpora_chunk_size | TBD
corpora_parts_count | TBD
output_dir | TBD

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
