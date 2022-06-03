import io
import logging
import mimetypes
import os
import urllib
import zipfile
from datetime import datetime

import pdfkit
import pyqrcode
from django.core.files.storage import default_storage
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
    'transfer-and-recovery': True,
    'academic-leave-return': True,
    'private-information-change': True,
    'expulsion': True,
    'key-card': True,
    'reference-student': True,
    'key-card-first': True
}

# Опции
# Тип обучения
education_types = [('Очное', 'Очное'), ('Заочное', 'Заочное')]

# Статусы заявлений/справок
application_statuses = [('Не проверено', 'Не проверено'), ('Отозвано на исправление', 'Отозвано на исправление'),
                        ('Подтверждено', 'Подтверждено'), ('Завершено', 'Завершено')]

# Статусы для модели HostelReferral
hostel_statuses = [('Не рассмотрено', 'Не рассмотрено'),
                   ('Одобрено', 'Одобрено'),
                   ('Отказано', 'Отказано'),
                   ('Заселен', 'Заселен'),
                   ('Выселен', 'Выселен'),
                   ('Неявка', 'Неявка')
                   ]

# Причины
reference_reasons = [('в связи с отчислением', 'в связи с отчислением'),
                     ('в связи с переводом в другой университет', 'в связи с переводом в другой университет')]

duplicate_types = [('Дубликат диплома', 'Дубликат диплома'),
                   ('Дубликат диплома с приложениями', 'Дубликат диплома с приложениями'),
                   ('Дубликат приложения', 'Дубликат приложения')]

duplicate_reasons = [('утерей', 'утерей'), ('порчей', 'порчей')]

academic_leave_reasons = [('по состоянию здоровья', 'по состоянию здоровья'),
                          ('с призывом на воинскую службу', 'с призывом на воинскую службу'),
                          ('с рождением ребенка', 'с рождением ребенка')]

foundation_types = [('на платной основе', 'на платной основе'),
                    ('на основе образовательного гранта', 'на основе образовательного гранта')]

information_change_reasons = [('в связи со сменой удостоверения личности', 'в связи со сменой удостоверения личности'),
                              ('в связи с вступлением в брак и сменой удостоверения личности',
                               'в связи с вступлением в брак и '
                               'сменой удостоверения личности')]

key_card_first_reasons = [
    ('в связи c восстановлением в число студентов', 'в связи c восстановлением в число студентов'),
    ('в связи c переводом из другого ВУЗа', 'в связи c переводом из другого ВУЗа')]

faculties = [('горный', 'Горный'),
             ('машиностроительный', 'Машиностроительный'),
             ('инновационных технологий', 'Инновационных технологий'),
             ('энергетиики, автоматики и телекоммуникаций', 'Энергетиики, автоматики и телекоммуникаций'),
             ('транспортно-дорожный', 'Транспортно-дорожный'),
             ('архитектурно-строительный', 'Архитектурно-строительный'),
             ('инженерной экономики и менеджмента', 'Инженерной экономики и менеджмента'),
             ('заочного и дистанционного обучения', 'Дистанционного обучения'),
             ('магистратура', 'Магистратура'),
             ('докторантура', 'Докторантура'),
             ('Колледж инновационных технологий КарТУ', 'Колледж инновационных технологий КарТУ'),
             ]

hostels = [('Общежитие №3', 'Общежитие №3'),

           ('Общежитие Жилищный комплекс «Армандастар Ордасы»',
            'Общежитие Жилищный комплекс «Армандастар Ордасы»'),

           ('Общежитие «Студенттер үйi»',
            'Общежитие «Студенттер үйi»')
           ]

semesters = [('весеннего', 'весеннего'),
             ('осеннего', 'осеннего')]

room_types = [('Мужская', 'Мужская'),
              ('Женская', 'Женская'),
              ('Неопределено', 'Неопределено')]

APPLICATIONS_TYPES = [('Академическая мобильность', 'Академическая мобильность'),
                      ('Общежитие', 'Общежитие'),
                      ('Дубликаты документов', 'Дубликаты документов'),
                      ('Академическая справка', 'Выдача транскрипта обучавшимся'),
                      ('Академический отпуск', 'Академический отпуск'),
                      ('Перевод в другой ВУЗ', 'Перевод в другой ВУЗ'),
                      ('Перевод в КарТУ', 'Перевод в КарТУ'),
                      ('Восстановление в число обучающихся', 'Восстановление в число обучающихся'),
                      ('Возвращение из акадического отпуска', 'Возвращение из акадического отпуска'),
                      ('Изменение персональных данных', 'Изменение персональных данных'),
                      ('Отчисление', 'Отчисление'),
                      ('Перевод внутри ВУЗа', 'Перевод внутри ВУЗа'),
                      ('Восстановление ключ-карты', 'Восстановление ключ-карты'),
                      ('Выдача транскрипта обучающимся', 'Выдача транскрипта обучающимся'),
                      ('Получение ключ-карты', 'Получение ключ-карты')
                      ]

languages_from = [('с русского языка', 'с русского языка'),
                  ('с государственного языка', 'с государственного языка')]

languages_to = [('на русский язык', 'на русский язык'),
                ('на государственный язык', 'на государственный язык')]

categories = [('Category1.1', 'Категория 1(Инвалиды)'),
              ('Category1.2', 'Категория 1(Сироты)'),
              ('Category2', 'Категория 2 (Кандас)'),
              ('Category3', 'Категория 3 (Серпын)'),
              ('Category4', 'Категория 4 (Многодетные)'),
              ('NoCategory', 'На общих основаниях')]

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
    msg = EmailMessage(subject='Центр обслуживания студентов КарТУ', body=message, to=to)
    msg.content_subtype = 'html'
    try:
        msg.send()
    except Exception as e:
        logger.exception(e)


# отправка письма с файлом
def send_email_with_attachment(mail_template, context, to, file):
    message = render_to_string(mail_template, context)
    msg = EmailMessage(subject='Центр обслуживания студентов КарТУ', body=message, to=to)
    msg.content_subtype = 'html'
    msg.attach(file.name, file.file.getvalue(), mimetypes.guess_type(file.name)[0])
    try:
        msg.send()
    except Exception as e:
        logger.exception(e)


# отправка письма с файлом
def send_email_with_attachment_file(mail_template, context, to, file):
    message = render_to_string(mail_template, context)
    msg = EmailMessage(subject='Центр обслуживания студентов КарТУ', body=message, to=to)
    msg.content_subtype = 'html'
    msg.attach_file(file)
    try:
        msg.send()
    except Exception as e:
        logger.exception(e)


# Генерация QR кода - альтернатива подписи, как верификация пользователя услуги
def generate_qr_code(url):
    qr = pyqrcode.create(url)
    return qr.png_as_base64_str(scale=4)


def download_referral_and_send(ctx, to):
    url = ctx['referral_url']
    response = urllib.request.urlopen(url)
    file = default_storage.open("hostel_referral.pdf", "wb")
    file.write(response.read())
    file.close()
    send_email_with_attachment_file("mails/hostel_referral.html", ctx, to, "media/hostel_referral.pdf")
    default_storage.delete("hostel_referral.pdf")
