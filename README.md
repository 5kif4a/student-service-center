# student-service-center
**_Центр обслуживания студентов КарГТУ_**\
Web-приложение реализованное на веб-фреймворке **Django**\
**Требования**\
Python 3.6+\
MySQL/sqlite(опционально)\
[RECAPTCHA V3](https://developers.google.com/recaptcha/docs/v3)\
Конвертер HTML в PDF [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html). Требуется для генерации PDF\
**Установка**
- Склонировать проект
```
git clone https://github.com/5kif4a/student-service-center.git
```
- Установить virtualenv при помощи pip
```
pip install virtualenv
```
- В директории проекта создать новую виртуальную среду
```
cd path_to_project
python3 -m venv venv
```
- Активировать виртуальную среду
```
Windows
venv\Scripts\activate.bat
Linux
source venv\bin\activate
```
- Установить требуемые зависимости
```
pip install -r requirements.txt
```
- На Windows для библиотеки mysqlclient требуется Microsoft Visual C++ 14.0 (или выше) - [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/ru/visual-cpp-build-tools/)
- Создайте файл .env в корне проекта и пропишите нужные параметры по примеру
```
DEBUG=on (для разработки оставьте on) 
SECRET_KEY=ваш_секретный_ключ_приложения
BASE_URL=базовый URL для генерации ссылки QR-кода, для тестирования в локальной сети запустить сервер Django с хостом 0.0.0.0
и вставить IP вашего компьютера в локальной сети

# подключение к СУБД MySQL, для подключения к другим СУБД смотрите здесь https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASE_URL=mysql://user:password@localhost:port/database
SQLITE_URL=sqlite:///db.sqlite3
PATH_WKHTMLTOPDF=путь к исполняемому файлу утилиты wkhtmltopdf

# настройки почтового сервера
DEFAULT_FROM_EMAIL=дефолтный адрес отправителя
SERVER_EMAIL=эмейл почтового сервера
EMAIL_HOST=smtp.gmail.com - для примера хост GMail, другие почтовые сервисы ищите в интернете
EMAIL_PORT=587
EMAIL_HOST_USER=электронная почта
EMAIL_HOST_PASSWORD=пароль от почты
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False

# Настройки баг-трекера Sentry, читайте https://docs.sentry.io/error-reporting/quickstart/?platform=python
DSN=Data Source Name
```
- Миграция базы данных
```
py manage.py magemigrations ssc 
py manage.py migrate
```
- Создание суперпользователя
```
py manage.py createsuperuser
для создания суперпользователя будут запрошеы
логин
пароль
email
```
- Запуск сервера Django
```
py manage.py runserver 8000
```
- Административная панель: 127.0.0.1:8000/admin
