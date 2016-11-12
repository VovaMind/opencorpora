Хотим разметить корпус онто-объектами. 

Данные берем из результатов соренования, проходившего в рамках конференции Диалог 2016.

Участники дали результаты для размеченных корпусов (тренировочного и тестовго) и для общего корпуса.

Нужно разметить общий корпус (https://www.dropbox.com/s/fja8gzpf59hfu1p/testset-v2.zip?dl=0), обучив композицию решений участников на размеченном корпусе.

Подробности о разметке: http://opencorpora.org/wiki/Nermanual/2

Размеченный корпус: https://github.com/dialogue-evaluation/factRuEval-2016

Текущий pipeline для получения разметки:
1. Выбираем набор признаков. Делаем его в FeaturesExtractor/features_extractor.py. Или можно использовать текущий набор признаков.
2. Построение моделей:
  1. Извлекаем признаки из рамеченного корпуса testset с помощью FeaturesExtractor/get_testset_features.py. (devset не подходит, так как участники его видели)
  2. Запускаем DataAnalysis/token_objects.R и потом DataAnalysis/token_span_types.R.
3. Извлечение признаков из всего корпуса: FeaturesExtractor/get_corpora_features.py.
4. Получаем объекты и спаны для всего корпуса: DataAnalysis/restore_full_corpus.R.
5. Получаем итоговую разметку: FeaturesExtractor/markup_builder.py.
