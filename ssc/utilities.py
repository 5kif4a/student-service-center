import os

from django.shortcuts import HttpResponse
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
    'abroad': True,
    'certificate': True,
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
             ('заочного и дистанционного обучения', 'заочного и дистанционного обучения')
             ]

hostels = [('Общежитие №1', 'Общежитие №1'),

           ('Общежитие Жилищный комплекс «Армандастар Ордасы»',
            'Общежитие Жилищный комплекс «Армандастар Ордасы»'),

           ('Общежитие «Серпіндестер Ордасы»',
            'Общежитие «Серпіндестер Ордасы»')
           ]

semesters = [('весеннего', 'весеннего'),
             ('осеннего', 'осеннего')]

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
def send_email(mail_template, context, to):
    message = render_to_string(mail_template, context)
    msg = EmailMessage(subject='Центр обслуживания студентов КарГТУ', body=message, to=to)
    msg.content_subtype = 'html'
    msg.send()


# Генерация QR кода - альтернатива подписи, как верификация пользователя услуги
def generate_qr_code(url):
    qr = pyqrcode.create(url)
    return qr.png_as_base64_str(scale=6)

