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
3. Перед запуском нужно скачать [w2v модель](http://rusvectores.org/static/models/rusvectores2/news_rusvectores2.bin.gz) (скопировать в FeaturesExtractor/scripts/data) и [mystem](https://tech.yandex.ru/mystem/) (скопировать в FeaturesExtractor/scripts/bin).
4. Нужно проверить, что тесты проходят. Для этого нужно перейти в FeaturesExtractor/test и запустить "python -m pytest". Должно пройти 16 тестов. 

ВАЖНО! В тестах предполагается, что w2v файл называется "news_win20.model.bin", а испольняемый файл для mystem называется "mystem.exe". В случае необходимости нужно заменить эти названия в тестах (py-файлы) и в конфигах (json-файлы).

# Основной pipeline для получения разметки:

* Подготвка словарей по devset. Мы извлекаем частотные слова для определенного типа спанов. Запуск:
```bash
python FeaturesExtractor/scripts/get_span_keywords.py config_file
```
Это нужно проделать только один раз. Важно извлекать данные из devset'а, чтобы избежать перееобучения на testset'е. Остальные газетиры нужно складывать в ту же директорию (words_set_dir в конфиге).
* Выбираем набор признаков. Делаем его в FeaturesExtractor/features_extractor.py. Или можно использовать текущий набор признаков.
* Построение моделей:
  1. Извлекаем признаки из рамеченного корпуса testset с помощью FeaturesExtractor/get_testset_features.py. (devset не подходит, так как участники его видели)
  2. Запускаем DataAnalysis/token_objects.R и потом DataAnalysis/token_span_types.R.
* Извлечение признаков из всего корпуса: FeaturesExtractor/get_corpora_features.py.
Для эффективности делаем извлечение признаков параллельно. Для этого нужно задать "parts_count" в common_config'е.
Также требуется запускать get_corpora_features с одним параметром - номер части (от 0 до parts_count - 1).
* Получаем объекты и спаны для всего корпуса: DataAnalysis/restore_full_corpus.R. 
Его нужно запускать как Rscript restore_full_corpus.R input_dir, где input_dir - каталог с извлеченными признаками.
Предполагается параллельный запуск скрипта для каждой из частей.
* Получаем итоговую разметку: FeaturesExtractor/markup_builder.py.
Также нужно запускать с параметром от 0 до parts_count - 1 для построения результата для конкретной части.
