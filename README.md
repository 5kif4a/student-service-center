# student-service-center
**_Центр обслуживания студентов КарГТУ_**\
Web-приложение реализованное на фреймворке **Django**\
**Требования**\
Python 3.6+\
MySQL/sqlite(опционально)\
[RECAPTCHA V3](https://developers.google.com/recaptcha/docs/v3)\
Конвертер HTML в PDF [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html). Обязателен для работы приложения\
**Установка**
- Скачать проект
```
git clone https://github.com/5kif4a/student-service-center.git
```
- Создать файл в папке проекта db.sqlite3
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
# cmd.exe
pip install -r requirements.txt
```
- На Windows для библиотеки mysqlclient требуется Microsoft Visual C++ 14.0 (или выше) - [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/ru/visual-cpp-build-tools/)
- Создайте файл .env в корне проекта и пропишите нужные параметры по примеру
```
DEBUG=True
SECRET_KEY=ваш_секретный_ключ

# подключение к БД MySQL
DATABASE_URL=mysql://user:password@localhost:port/database
SQLITE_URL=sqlite:///db.sqlite3

RECAPTCHA_PUBLIC_KEY=публичный ключ recaptcha
RECAPTCHA_PRIVATE_KEY=приватный ключа recaptcha

DEFAULT_FROM_EMAIL=дефолтный адрес отправителя
SERVER_EMAIL=эмейл почтового сервера
EMAIL_HOST=smtp.gmail.com - для примера хост GMail, другие почтовые сервисы ищите в интернете
EMAIL_PORT=587
EMAIL_HOST_USER=электронная почта
EMAIL_HOST_PASSWORD=пароль от почты
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False

PATH_WKHTMLTOPDF=path_to_wkhtmltopdf
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
Административная панель: 127.0.0.1:8000/admin\
Запустить сервер
```
py manage.py runserver 8000
```

