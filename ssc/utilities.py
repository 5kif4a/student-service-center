from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import pdfkit
import pyqrcode
from SSC_KSTU.settings import env
import logging


# Путь к .exe файлу генерирующий PDF
PATH_WKHTMLTOPDF = env.str('PATH_WKHTMLTOPDF')

# Статусы разработки услуг
# True - готово | False - в разработке
statuses = {
    'bachelor': False,
    'postgraduate': False,
    'abroad': False,
    'certificate': False,
    'hostel': True,
    'duplicate': True,
    'reference': True,
    'academic-leave': True,
    'transfer-and-recovery': False
}

# Опции
# Тип обучения
education_types = [('Очное', 'Очное'), ('Заочное', 'Заочное')]

# Статусы заявлений/справок
application_statuses = [('Не проверено', 'Не проверено'), ('Отозвано на исправление', 'Отозвано на исправление'),
                        ('Подтверждено', 'Подтверждено'), ('Завершено', 'Завершено')]

# Причины
reference_reasons = [('В связи с отчислением', 'В связи с отчислением'),
                     ('В связи с переводом в другой университет', 'В связи с переводом в другой университет')]
duplicate_types = [('Дубликат диплома', 'Дубликат диплома'),
                   ('Дубликат диплома с приложениями', 'Дубликат диплома с приложениями'),
                   ('Дубликат приложения', 'Дубликат приложения')]
duplicate_reasons = [('Утеря', 'Утеря'), ('Порча', 'Порча')]
academic_leave_reasons = [('По состоянию здоровья', 'По состоянию здоровья'),
                          ('В связи с призывом на воинскую службу', 'В связи с призывом на воинскую службу'),
                          ('С рождением ребенка', 'С рождением ребенка')]


# Логирование
logger = logging.getLogger('SSC_KSTU')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('console.log')
formatter = logging.Formatter('%(name)s: [%(levelname)s] - %(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


# генерация заявления в PDF формате
def render_pdf(template, context):
    html = render_to_string(template, context=context)
    cfg = pdfkit.configuration(wkhtmltopdf=bytes(PATH_WKHTMLTOPDF, 'utf8'))
    pdf = pdfkit.from_string(html, False, configuration=cfg)
    response = HttpResponse(pdf, content_type='application/pdf')
    return response


# отправка письма
def send_email(message, to):
    msg = EmailMessage(subject='Центр обслуживания студентов', body=message, to=to)
    msg.send()


# Генерация QR кода - альтернатива подписи, как верификация пользователя услуги
def generate_qr_code(url):
    qr = pyqrcode.create(url)
    return qr.png_as_base64_str(scale=6)
