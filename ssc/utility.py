from django.shortcuts import HttpResponse
from django.template.loader import render_to_string
import pdfkit

PATH_WKHTMLTOPDF = r"D:\wkhtmltopdf\bin\wkhtmltopdf.exe"

statuses = {
    'bachelor': False,
    'postgraduate': False,
    'abroad': False,
    'certificate': False,
    'hostel': True,
    'duplicate': False,
    'reference': True,
    'academic-leave': False,
    'transfer-and-recovery': False
}


def render_pdf(template, context):
    html = render_to_string(template, context=context)
    cfg = pdfkit.configuration(wkhtmltopdf=bytes(PATH_WKHTMLTOPDF, 'utf8'))
    pdf = pdfkit.from_string(html, False, configuration=cfg)
    response = HttpResponse(pdf, content_type='application/pdf')
    return response
