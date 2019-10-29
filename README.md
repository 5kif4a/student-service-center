# student-service-center
**_Центр обслуживания студентов КарГТУ_**\
Web-приложение реализованное на фреймворке **Django**\
**Требования**\
Python 3.6+\
MySQL(опционально)\
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
- MySQL в качестве базы данных\
создать файл db.config в папке проекта\
файл конфигурации для коннектора базы
```
[client]
host = HOST
port = 3306
database = DATABASE_NAME
user = USER
password = PASSWORD
default-character-set = utf8
```
- В модуле ssc/utility.py прописать путь к wkhtmltopdf.exe
```
PATH_WKHTMLTOPDF = r"path_to_wkhtmltopdf\...\bin\wkhtmltopdf.exe"
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
- [ ] Конфигурацию переменными окружения
- [ ] Логирование
- [x] Генерация PDF
- [x] Hash id, hash names for media files 
- [ ] Email notifications for students
- [ ] Push notifications for moderators

