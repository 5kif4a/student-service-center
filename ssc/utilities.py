import io
import logging
import mimetypes
import os
import zipfile
from datetime import datetime

import pdfkit
import pyqrcode
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string

from SSC_KSTU.settings import env

# Путь к .exe файлу генерирующий PDF
PATH_WKHTMLTOPDF = env.str('PATH_WKHTMLTOPDF')

# Статусы разработки услуг
# True - готово | False - в разработке
statuses = {
    'bachelor': True,
    'postgraduate': True,
    'abroad': True,
    'certificate': True,
    'hostel': True,
    'duplicate': True,
    'reference': True,
    'academic-leave': True,
    'transfer-and-recovery': True
}

# Опции
# Тип обучения
education_types = [('Очное', 'Очное'), ('Заочное', 'Заочное')]

# Статусы заявлений/справок
application_statuses = [('Не проверено', 'Не проверено'), ('Отозвано на исправление', 'Отозвано на исправление'),
                        ('Подтверждено', 'Подтверждено'), ('Завершено', 'Завершено')]

# Статусы для модели HostelReferral
hostel_statuses = [('Не рассмотрено', 'Не рассмотрено'),
                   ('Подтверждено', 'Подтверждено'),
                   ('Отказано', 'Отказано'),
                   ('Заселен', 'Заселен'),
                   ('Выселен', 'Выселен'),
                   ]

# Причины
reference_reasons = [('В связи с отчислением', 'В связи с отчислением'),
                     ('В связи с переводом в другой университет', 'В связи с переводом в другой университет')]

duplicate_types = [('Дубликат диплома', 'Дубликат диплома'),
                   ('Дубликат диплома с приложениями', 'Дубликат диплома с приложениями'),
                   ('Дубликат приложения', 'Дубликат приложения')]

duplicate_reasons = [('утерей', 'утерей'), ('порчей', 'порчей')]

academic_leave_reasons = [('по состоянию здоровья', 'по состоянию здоровья'),
                          ('с призывом на воинскую службу', 'с призывом на воинскую службу'),
                          ('с рождением ребенка', 'с рождением ребенка')]

foundation_types = [('на платной основе', 'на платной основе'),
                    ('на основе образовательного гранта', 'на основе образовательного гранта')]

faculties = [('горный', 'горный'),
             ('машиностроительный', 'машиностроительный'),
             ('инновационных технологий', 'инновационных технологий'),
             ('энергетиики, автоматики и телекоммуникаций', 'энергетиики, автоматики и телекоммуникаций'),
             ('транспортно-дорожный', 'транспортно-дорожный'),
             ('архитектурно-строительный', 'архитектурно-строительный'),
             ('инженерной экономики и менеджмента', 'инженерной экономики и менеджмента'),
             ('заочного и дистанционного обучения', 'заочного и дистанционного обучения'),
             ('магистратура', 'магистратура'),
             ('докторантура', 'докторантура'),
             ]

hostels = [('Общежитие №1', 'Общежитие №1'),

           ('Общежитие Жилищный комплекс «Армандастар Ордасы»',
            'Общежитие Жилищный комплекс «Армандастар Ордасы»'),

           ('Общежитие «Серпіндестер Ордасы»',
            'Общежитие «Серпіндестер Ордасы»')
           ]

semesters = [('весеннего', 'весеннего'),
             ('осеннего', 'осеннего')]

room_types = [('Мужская', 'Мужская'),
              ('Женская', 'Женская'),
              ('Пустая', 'Пустая')]

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
    response['Content-Disposition'] = 'filename="application.pdf"'
    return response


# сгенерировать архив с прикрепленными файлами
def make_zip_response(filenames):
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
        for filename in filenames:
            zip_file.write(filename, os.path.split(filename)[1])

    zip_filename = f'{datetime.now().strftime("%m-%d-%Y - %H:%M:%S")}.zip'
    response = HttpResponse(zip_io.getvalue(), content_type='application/x-zip-compressed')
    response['Content-Disposition'] = f"attachment;filename*=UTF-8''{zip_filename}"
    response['Content-Length'] = zip_io.tell()
    return response


# отправка письма
def send_email(mail_template, context, to):
    message = render_to_string(mail_template, context)
    msg = EmailMessage(subject='Центр обслуживания студентов КарГТУ', body=message, to=to)
    msg.content_subtype = 'html'
    msg.send()


# отправка письма с файлом
def send_email_with_attachment(mail_template, context, to, file):
    message = render_to_string(mail_template, context)
    msg = EmailMessage(subject='Центр обслуживания студентов КарГТУ', body=message, to=to)
    msg.content_subtype = 'html'
    msg.attach(file.name, file.file.getvalue(), mimetypes.guess_type(file.name)[0])
    msg.send()


# Генерация QR кода - альтернатива подписи, как верификация пользователя услуги
def generate_qr_code(url):
    qr = pyqrcode.create(url)
    return qr.png_as_base64_str(scale=6)
