# search-engine

## Статус сдачи

Принята преподавателем | Сделана, но не проверена | Не сделана
------------- | ------------- | --------------
:heavy_check_mark: | :black_square_button: | :x:

| Задача | Статус |
|---|---|
|Задание 1| :black_square_button:  |
|Задание 2| :black_square_button:  |
|Задание 3| :black_square_button:  |

## Prerequisites
* Python 3.7 и выше  
* Установленный pip  
* `pip install -r requirements.txt`

Реультаты выполнения программ в папке *resources*   
### Задача 1
Пакет *crawler*   
Сохраняются не сами html страницы, а необходимое нам содержимое:

* Заголовок вопроса
* Сам вопрос
* Тэги вопроса
* Ответы на вопрос
* Комментарии к ответам и вопросу

  ```
  cd crawler
  python scrapper.py
  ```
### Задача 2   
Пакет *semantic*
```
cd semantic
python tokenizer.py
```
### Задача 3     
Пакет *semantic*   
Первый запрос идет долго (привратности питона судя по всему). Первый скрипт создает индекс файл, второй нужен для поиска.   
```
cd semantic
python index.py
python engine.py
```