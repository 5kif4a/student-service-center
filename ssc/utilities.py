from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import pdfkit
import pyqrcode
from SSC_KSTU.settings import env

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
    'academic-leave': False,
    'transfer-and-recovery': False
}


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
