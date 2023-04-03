# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

Предлагаемое приложение - небольшая социальная сеть.
Пользователи могут просматривать посты других пользователей (доступно всем пользователям).
Зарегистрированные пользователи могут оставлять публикации (посты) на своей странице,комментировать чужие записи, подписываться на обновление других авторов.


### Использованные технологии:

Python 3.7

sqlite3

Django 2.2.16

sorl-thumbnail 12.7.0

bootstrap 4

## Установка

Чтоб развернуть проект на локальной машине клонируйте репозиторий 

```git clone git@github.com:Krugger1982/hw05_final.git```

#### Установите и активируйте виртуальное окружение.  

Cоздание виртуального окружения:  
```
$ python3 -m venv venv
```

Активация виртуального окружения:  
```$ source venv/bin/activate``` (команда для Linux/MacOS)  
или:  
```$ source venv/Scripts/activate``` (команда для Windows)  

при активированном виртуальном окружении выполните команду: 

```$ pip install -r requirements.txt ```


# Запуск сервера на локальной машине 
В папке hw05_final/yatube/ выполните команду запуска сервера:  

```$ python3 manage.py runserver ```  

Сервер запустится по адресу: http://127.0.0.1

Перейдите по этому адресу - вы окажетесь на главной странице проекта.

Рабочая версия веб-сайта развернута [здесь](http://krugger1.pythonanywhere.com/)

Автор: [Алексей Разумовский](https://vk.com/razumovsky1982) 
