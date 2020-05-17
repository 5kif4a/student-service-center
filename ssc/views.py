from django.shortcuts import render, render_to_response, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.views import View
from django.http import JsonResponse
from django.core import serializers
from ssc.forms import *
from ssc.models import *
from ssc.utilities import *
from SSC_KSTU.settings import DEBUG, BASE_URL
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import json
from django.shortcuts import get_object_or_404

# Create your views here.

# Текущий ректор
try:
    rector_name = Rector.objects.filter(status=True)[0].name
except:
    rector_name = 'Ибатову Марату Кенесовичу'


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
    app_type = None
    app_ref = None

    def get(self, request):
        form = self.form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        self.context['form'] = form

        files = request.FILES
        fs = FileSystemStorage()

        if form.is_valid():
            for _, file in files.items():
                fs.save(file.name, file)
            data = form.save()

            # создаем уведомление
            base_url = get_current_site(request)
            url_for_app = f'{base_url}/admin/ssc/{self.app_ref}/{data.id}/change/'

            n = Notification(application_type=self.app_type, url_for_application=url_for_app)
            n.save()

            return render(request, 'ssc/complete.html')

        if DEBUG:
            print(form.errors)

        return render(request, self.template_name, self.context)


def bachelor(request):
    context = {
        'status': statuses.get('bachelor')
    }
    return render(request, 'ssc/bachelor.html', context)


def postgraduate(request):
    context = {
        'status': statuses.get('postgraduate')
    }
    return render(request, 'ssc/postgraduate.html', context)


class AbroadView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Прием документов для участия в конкурсе на обучение за рубежом, в том числе академической мобильности"
    Государственная услуга
    """
    form_class = AbroadForm
    template_name = 'ssc/abroad.html'
    context = {'status': statuses.get('abroad')}
    app_type = 'Академическая мобильность'
    app_ref = 'abroad'

    @login_required
    def render(self, obj_id):
        app = Abroad.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=abroad&id={obj_id}')
            }
            return render_pdf('applications/abroad.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


def certificate(request):
    context = {
        'status': statuses.get('certificate')
    }
    return render(request, 'ssc/certificate.html', context)


class HostelView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Предоставление общежития обучающимся в высших учебных заведениях"
    Государственная услуга
    """
    form_class = HostelForm
    template_name = 'ssc/hostel.html'
    context = {'status': statuses.get('hostel')}
    app_type = 'Общежитие'
    app_ref = 'hostel'

    @login_required
    def render(self, obj_id):
        app = Hostel.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=hostel&id={obj_id}')
            }
            return render_pdf('applications/hostel.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


class DuplicateView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Выдача справки лицам, не завершившим высшее и послевузовское образование"
    Государственная услуга
    """
    # form_class = DuplicateForm
    template_name = 'ssc/duplicate.html'
    context = {'status': statuses.get('duplicate')}
    # mail_template = 'mails/duplicate.html'
    app_type = 'Дубликаты документов'
    app_ref = 'duplicate'

    def get(self, request):
        # form = self.form_class()
        # self.context['form'] = form
        return render(request, self.template_name, self.context)

    # @login_required
    # def render(self, obj_id):
    #     app = Duplicate.objects.get(id=obj_id)
    #     if app.status not in ('Не проверено', 'Отозвано на исправление'):
    #         context = {
    #             'rector_name': rector_name,
    #             'app': app,
    #             'qr_code': generate_qr_code('http://www.kstu.kz/')
    #         }
    #         return render_pdf('applications/duplicate.html', context)
    #     else:
    #         return HttpResponse('<center><h1>Заявление не потверждено</h1></center>')


class AcademicLeaveView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Предоставление академических отпусков обучающимся в организациях образования"
    Государственная услуга
    """
    form_class = AcademicLeaveForm
    template_name = 'ssc/academic-leave.html'
    context = {'status': statuses.get('academic-leave')}
    app_type = 'Академический отпуск'
    app_ref = 'academicleave'

    @login_required
    def render(self, obj_id):
        app = AcademicLeave.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=academic_leave&id={obj_id}')
            }
            return render_pdf('applications/academic-leave.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


class ReferenceView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Выдача справки лицам, не завершившим высшее и послевузовское образование"
    Государственная услуга
    """
    form_class = ReferenceForm
    template_name = 'ssc/reference.html'
    context = {'status': statuses.get('reference')}
    app_type = "Академическая справка"
    app_ref = "reference"

    @login_required
    def render(self, obj_id):
        app = Reference.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=reference&id={obj_id}')
            }
            return render_pdf('applications/reference.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


def transfer_and_recovery(request):
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
    context = {}
    app_type = "Перевод в другой ВУЗ"
    app_ref = 'transfer'

    @login_required
    def render(self, obj_id):
        app = Transfer.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=transfer&id={obj_id}')
            }
            return render_pdf('applications/transfer.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


class TransferKSTUView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Перевод в КарГТУ"
    Внутривузовская услуга
    """
    form_class = TransferKSTUForm
    template_name = 'ssc/transfer-kstu.html'
    context = {}
    app_type = 'Перевод в КарГТУ'
    app_ref = 'transferkstu'

    @login_required
    def render(self, obj_id):
        app = TransferKSTU.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=transfer_kstu&id={obj_id}')
            }
            return render_pdf('applications/transfer-kstu.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


class RecoveryView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Восстановление в число обучающихся"
    Внутривузовская услуга
    """
    form_class = RecoveryForm
    template_name = 'ssc/recovery.html'
    context = {}
    app_type = 'Восстановление в число обучающихся'
    app_ref = 'recovery'

    @login_required
    def render(self, obj_id):
        app = Recovery.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'rector_name': rector_name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=recovery&id={obj_id}')
            }
            return render_pdf('applications/recovery.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


@login_required
def get_notifications(request):
    """
    Получить все уведомления
    """
    notifications = Notification.objects.filter(is_showed=False).order_by('-date')
    notifications = serializers.serialize("json", notifications)
    data = json.loads(notifications, encoding='utf8')
    return JsonResponse(data, safe=False)


# отметить уведомление как прочитанное
def mark_as_read(request, obj_id):
    n = Notification.objects.get(id=obj_id)
    n.is_showed = True
    n.save()
    return HttpResponse("OK", status=200)


@login_required(login_url='/admin/login')
def stats(request):
    """
    Выгрузка по статистике
    """
    template = 'custom_admin/stats.html'
    return render(request, template)


def page_not_found(request, exception):
    return render(request, template_name='error_handlers/404.html', status=404)


def internal_server_error(request):
    return render(request, template_name='error_handlers/500.html', status=500)


def check_order(request):
    """
    Проверка
    заявления
    """
    template = 'ssc/verification.html'
    model_dictionary = {'academic_leave': AcademicLeave,
                        'hostel': Hostel,
                        'reference': Reference,
                        'abroad': Abroad,
                        'transfer_kstu': TransferKSTU,
                        'transfer': Transfer,
                        'recovery': Recovery}

    if request.method == 'GET':
        order_type = request.GET.get('order_type')
        order_id = request.GET.get('id')

        if order_type is None or order_id is None:
            return page_not_found(request, 'Не существует')

        model = model_dictionary[order_type]
        obj = get_object_or_404(model, id=order_id)

        order_type = model._meta.verbose_name.capitalize()

        context = {'last_name': obj.last_name,
                   'first_name': obj.first_name,
                   'patronymic': obj.patronymic,
                   'individual_identification_number': obj.individual_identification_number,
                   'date': obj.date_of_application,
                   'type': order_type}

        return render(request, template, context)

    return page_not_found(request, 'Не существует')



