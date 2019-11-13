from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from ssc.forms import *
from ssc.models import *
from ssc.utilities import *
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
# Create your views here.

# Текущий ректор
rector_name = Rector.objects.filter(status=True)[0].name


# главная страница
def index(request):
    return render(request, 'ssc/index.html')


# Прием документов и зачисление в высшие учебные заведения для обучения
# по образовательным программам высшего образования
def bachelor(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('bachelor')
        }
        return render(request, 'ssc/bachelor.html', context)


def postgraduate(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('postgraduate')
        }
        return render(request, 'ssc/postgraduate.html', context)


def abroad(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('abroad')
        }
        return render(request, 'ssc/abroad.html', context)


def certificate(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('certificate')
        }
        return render(request, 'ssc/certificate.html', context)


def hostel(request):
        if request.method == 'POST':
            return redirect('')
        else:
            # form = ReferenceForm()
            context = {
                # 'form': form
                'status': statuses.get('hostel')
            }
            return render(request, 'ssc/hostel.html', context)


class DuplicateView(View):
    """
    Представления для подачи заявления по услуге
    "Выдача справки лицам, не завершившим высшее и послевузовское образование"
    Государственная услуга
    """
    form_class = DuplicateForm
    template_name = 'ssc/duplicate.html'
    context = {'status': statuses.get('duplicate')}

    def get(self, request):
        form = self.form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        self.context['form'] = form

        file = request.FILES['iin_attachment']
        fs = FileSystemStorage()

        if form.is_valid():
            fs.save(file.name, file)
            form.save()

            message = f'{request.POST.get("first_name")}, Ваше заявление принято. Дубликат будет готов в течение 30 дней. ' \
                'Как только дубликат будет готов, на Вашу почту придет повторное уведомление.\n' \
                'Пожалуйста, не отвечайте на это письмо. ' \
                'Если у Вас возникнут вопросы, ' \
                'просим обращаться по номеру 8(7212)56-59-32 (внутренний 2023) или в КарГТУ, 1 корпус, кабинет № 109. ' \
                'Если Вы получили это письмо по ошибке, пожалуйста, сообщите нам об этом.\n' \
                '__\n' \
                'С уважением, Центр Обслуживания Студентов КарГТУ.'

            send_email(message, (request.POST.get('email', ''),))

            return render(request, 'ssc/complete.html')
        return render(request, self.template_name, self.context)

    @login_required
    def render(self, obj_id):
        app = Duplicate.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code('http://www.kstu.kz/')
            }
            return render_pdf('applications/duplicate.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено</h1></center>')


class AcademicLeaveView(View):
    """
    Представления для подачи заявления по услуге
    "Предоставление академических отпусков обучающимся в организациях образования"
    Государственная услуга
    """
    form_class = AcademicLeaveForm
    template_name = 'ssc/academic-leave.html'
    context = {'status': statuses.get('academic-leave')}

    def get(self, request):
        form = self.form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        self.context['form'] = form

        file = request.FILES['attachment']
        fs = FileSystemStorage()

        if form.is_valid():
            fs.save(file.name, file)
            form.save()

            message = f'{request.POST.get("first_name")}, Ваше заявление принято. ' \
                'Просим Вас обязательно в течение 2 дней сдать в КарГТУ, 1 корпус, кабинет № 109 следующие документы:\n' \
                '1. оригинал СПРАВКИ ВКК – при уходе в академический отпуск по болезни;\n' \
                '2. оригинал ПОВЕСТКИ, либо СПРАВКА О ПРИЗЫВЕ С ВОЕНКОМАТА – в связи с призывом на воинскую службу.\n' \
                'В случае не сдачи оригинала документа академический отпуск оформлен не будет.\n' \
                'Приказ о предоставлении академического отпуска будет готов в течение 3 дней.\n' \
                'Пожалуйста, не отвечайте на это письмо. Если у Вас возникнут вопросы, ' \
                'просим обращаться по номеру 8(7212)56-59-32 (внутренний 2023) или в КарГТУ, 1 корпус, кабинет № 109.' \
                'Если Вы получили это письмо по ошибке, пожалуйста, сообщите нам об этом.\n' \
                '__\n' \
                'С уважением, Центр Обслуживания Студентов КарГТУ.'

            send_email(message, (request.POST.get('email', ''),))

            return render(request, 'ssc/complete.html')
        return render(request, self.template_name, self.context)

    @login_required
    def render(self, obj_id):
        app = AcademicLeave.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code('http://www.kstu.kz/')
            }
            return render_pdf('applications/academic-leave.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено</h1></center>')


class ReferenceView(View):
    """
    Представления для подачи заявления по услуге
    "Выдача справки лицам, не завершившим высшее и послевузовское образование"
    Государственная услуга
    """
    form_class = ReferenceForm
    template_name = 'ssc/reference.html'
    context = {'status': statuses.get('reference')}

    def get(self, request):
        form = self.form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        self.context['form'] = form

        file = request.FILES['iin_attachment']
        fs = FileSystemStorage()

        if form.is_valid():
            fs.save(file.name, file)
            form.save()

            message = f'{request.POST.get("first_name")}, Ваше заявление принято. Справка будет готова в течение 10 дней. ' \
                'Как только справка будет готова, на Вашу почту придет повторное уведомление.\n\n' \
                'Пожалуйста, не отвечайте на это письмо.' \
                'Если у Вас возникнут вопросы, ' \
                'просим обращаться по номеру 8(7212)56-59-32 (внутренний 2023) или в КарГТУ, 1 корпус, кабинет № 109. ' \
                'Если Вы получили это письмо по ошибке, пожалуйста, сообщите нам об этом.\n' \
                '__\n' \
                'С уважением,' \
                'Центр Обслуживания Студентов КарГТУ.'

            send_email(message, (request.POST.get('email', ''),))

            return render(request, 'ssc/complete.html')
        return render(request, self.template_name, self.context)

    @login_required
    def render(self, obj_id):
        app = Reference.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code('http://www.kstu.kz/')
            }
            return render_pdf('applications/reference.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено</h1></center>')


def transfer_and_recovery(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('transfer-and-recovery')
        }
        return render(request, 'ssc/transfer-and-recovery.html')

