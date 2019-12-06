from django.shortcuts import render, render_to_response, redirect
from django.views import View
from ssc.forms import *
from ssc.models import *
from ssc.utilities import *
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
# Create your views here.

# Текущий ректор
# rector_name = Rector.objects.filter(status=True)[0].name


# главная страница
def index(request):
    return render(request, 'ssc/index.html')


class TemplateView(View):
    """
    Шаблон класс-представление
    """
    form_class = None
    template_name = None
    context = None
    mail_template = None

    def get(self, request):
        form = self.form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        self.context['form'] = form

        files = request.FILES
        fs = FileSystemStorage()

        print(form.errors)
        if form.is_valid():
            for _, file in files.items():
                fs.save(file.name, file)
            form.save()

            ctx = {'name': request.POST['first_name']}
            to = (request.POST.get('email', ''),)

            send_email(self.mail_template, ctx, to)

            return render(request, 'ssc/complete.html')
        return render(request, self.template_name, self.context)


def bachelor(request):
    if request.method == 'POST':
        return redirect('')
    else:
        context = {
            'status': statuses.get('bachelor')
        }
        return render(request, 'ssc/bachelor.html', context)


def postgraduate(request):
    if request.method == 'POST':
        return redirect('')
    else:
        context = {
            'status': statuses.get('postgraduate')
        }
        return render(request, 'ssc/postgraduate.html', context)


def abroad(request):
    if request.method == 'POST':
        return redirect('')
    else:
        context = {
            'status': statuses.get('abroad')
        }
        return render(request, 'ssc/abroad.html', context)


def certificate(request):
    if request.method == 'POST':
        return redirect('')
    else:
        context = {
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


class DuplicateView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Выдача справки лицам, не завершившим высшее и послевузовское образование"
    Государственная услуга
    """
    form_class = DuplicateForm
    template_name = 'ssc/duplicate.html'
    context = {'status': statuses.get('duplicate')}
    mail_template = 'mails/duplicate.html'

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


class AcademicLeaveView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Предоставление академических отпусков обучающимся в организациях образования"
    Государственная услуга
    """
    form_class = AcademicLeaveForm
    template_name = 'ssc/academic-leave.html'
    context = {'status': statuses.get('academic-leave')}
    mail_template = 'mails/academic-leave.html'

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


class ReferenceView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Выдача справки лицам, не завершившим высшее и послевузовское образование"
    Государственная услуга
    """
    form_class = ReferenceForm
    template_name = 'ssc/reference.html'
    context = {'status': statuses.get('reference')}
    mail_template = 'mails/reference.html'

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
        context = {
            'status': statuses.get('transfer-and-recovery')
        }
        return render(request, 'ssc/transfer-and-recovery.html', context)


class TransferView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Перевод в другой ВУЗ"
    Внутривузовская услуга
    """
    form_class = TransferForm
    template_name = 'ssc/transfer.html'
    mail_template = 'mails/transfer.html'
    context = {}

    @login_required
    def render(self, obj_id):
        app = Transfer.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code('http://www.kstu.kz/')
            }
            return render_pdf('applications/transfer.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено</h1></center>')


class TransferKSTUView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Перевод в КарГТУ"
    Внутривузовская услуга
    """
    form_class = TransferKSTUForm
    template_name = 'ssc/transfer-kstu.html'
    mail_template = 'mails/transfer-kstu.html'
    context = {}

    @login_required
    def render(self, obj_id):
        app = TransferKSTU.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code('http://www.kstu.kz/')
            }
            return render_pdf('applications/transfer-kstu.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено</h1></center>')


class RecoveryView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Восстановление в число обучающихся"
    Внутривузовская услуга
    """
    form_class = RecoveryForm
    template_name = 'ssc/recovery.html'
    mail_template = 'mails/recovery.html'
    context = {}

    @login_required
    def render(self, obj_id):
        app = Recovery.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code('http://www.kstu.kz/')
            }
            return render_pdf('applications/recovery.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено</h1></center>')


def page_not_found(request, exception):
    return render(request, template_name='error_handlers/404.html', status=404)


def internal_server_error(request):
    return render(request, template_name='error_handlers/500.html', status=500)

