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
- Проект создавался на платформе Windows\
Установку виртуальной среды на других платформах можно посмотреть на странице официальной [документации](https://docs.python.org/3/library/venv.html)
- В директории проекта создать новую виртуальную среду
```
# cmd.exe
cd path_to_project
py -m venv venv
```
- Активировать виртуальную среду
```
# cmd.exe
venv\Scripts\activate.bat
```
- Установить требуемые зависимости
```
# cmd.exe
pip install -r requirements.txt
```
- Создайте файл .env в корне проекта и пропишите нужные параметры по примеру
```
DEBUG=True
SECRET_KEY=ваш_секретный_ключ

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

PATH_WKHTMLTOPDF=path_to\...\wkhtmltopdf\bin\wkhtmltopdf.exe
```
- Миграция базы данных
```
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
**TODO LIST**
- [x] Поиск в базе данных
- [x] Фильтрация
- [x] Конфигурацию переменными окружения
- [ ] Логирование
- [x] Генерация PDF
- [x] Hash id, hash names for media files 
- [x] Email notifications for students
- [ ] Push notifications for moderators

