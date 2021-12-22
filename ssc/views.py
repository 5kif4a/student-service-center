from django.contrib import messages
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect
from django.core import serializers
from django.db.models import Q
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
        ctx = {}
        to = (request.POST.get('email', ''),)
        # try:
        #     send_email("mails/email_verification.html", ctx, to)
        # except:
        #     form = self.form_class()
        #     self.context['form'] = form
        #     messages.info(request, 'Вы ввели несуществующий email')
        #     return render(request, self.template_name, self.context)

        form = self.form_class(request.POST, request.FILES)
        self.context['form'] = form

        files = request.FILES
        fs = FileSystemStorage()

        if form.is_valid():
            # for _, file in files.items():
            #    fs.save(file.name, file)
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


def about(request):
    return render(request, 'ssc/about.html')


def state(request):
    return render(request, 'ssc/state.html')


def education(request):
    return render(request, 'ssc/education.html')


def online(request):
    return render(request, 'ssc/online.html')


def self(request):
    return render(request, 'ssc/self.html')


def stuff(request):
    return render(request, 'ssc/stuff.html')


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
                'stuff_position': Stuff.objects.get(application_type='Академическая мобильность').position,
                'stuff_name': Stuff.objects.get(application_type='Академическая мобильность').name,
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

    def get(self, request):
        form = self.form_class()
        if request.GET.__contains__('lang'):
            if request.GET.__getitem__('lang') == 'kz':
                self.template_name = "ssc/hostel_kz.html"
                form.localize()

        self.context['form'] = form
        return render(request, self.template_name, self.context)

    @login_required
    def render(self, obj_id):
        app = Hostel.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):

            vac = False
            death = False
            large = False
            disabled = False
            kandas = False

            if app.attachmentProperty:
                vac = True

            if app.attachmentDeath:
                death = True

            if app.attachmentLarge:
                large = True

            if app.attachmentDisabled:
                disabled = True

            if app.attachmentKandas:
                kandas = True

            context = {
                'stuff_position': Stuff.objects.get(application_type='Общежитие').position,
                'stuff_name': Stuff.objects.get(application_type='Общежитие').name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=hostel&id={obj_id}'),
                'death': death,
                'large': large,
                'disabled': disabled,
                'kandas': kandas,
                'vac': vac
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
    #             'stuff_position': Stuff.objects.get(application_type='Дубликаты документов').position,
    #             'stuff_name': Stuff.objects.get(application_type='Дубликаты документов').name,
    #             'app': app,
    #             'qr_code': generate_qr_code('http://www.kstu.kz/')
    #         }
    #         return render_pdf('applications/duplicate.html', context)
    #     else:
    #         return HttpResponse('<center><h1>Заявление не потверждено</h1></center>')


class AcademicLeaveView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Предоставление и продление академических отпусков обучающимся в организациях образования"
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

            documents = {
                'по состоянию здоровья': 'Справка ВКК',
                'с призывом на воинскую службу': 'Справка из военкомата о призыве',
                'с рождением ребенка': 'Копия свидетельства о рождении ребенка'
            }

            context = {
                'stuff_position': Stuff.objects.get(application_type='Академический отпуск').position,
                'stuff_name': Stuff.objects.get(application_type='Академический отпуск').name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=academic_leave&id={obj_id}'),
                'document': documents[app.reason]
            }
            if not app.is_prolongation:
                return render_pdf('applications/academic-leave.html', context)
            else:
                return render_pdf('applications/academic-leave-prolongation.html', context)
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
                'stuff_position': Stuff.objects.get(application_type='Академическая справка').position,
                'stuff_name': Stuff.objects.get(application_type='Академическая справка').name,
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
                'stuff_position': Stuff.objects.get(application_type='Перевод в другой ВУЗ').position,
                'stuff_name': Stuff.objects.get(application_type='Перевод в другой ВУЗ').name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=transfer&id={obj_id}')
            }
            return render_pdf('applications/transfer.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


class TransferKSTUView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Перевод в КарТУ"
    Внутривузовская услуга
    """
    form_class = TransferKSTUForm
    template_name = 'ssc/transfer-kstu.html'
    context = {}
    app_type = 'Перевод в КарТУ'
    app_ref = 'transferkstu'

    @login_required
    def render(self, obj_id):
        app = TransferKSTU.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'stuff_position': Stuff.objects.get(application_type='Перевод в КарТУ').position,
                'stuff_name': Stuff.objects.get(application_type='Перевод в КарТУ').name,
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
                'stuff_position': Stuff.objects.get(application_type='Восстановление в число обучающихся').position,
                'stuff_name': Stuff.objects.get(application_type='Восстановление в число обучающихся').name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=recovery&id={obj_id}')
            }
            return render_pdf('applications/recovery.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


class HostelReferralView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Направление в общежитие в учебных заведениях"
    Государственная услуга
    """
    form_class = HostelReferralForm
    template_name = 'ssc/hostel_referral.html'
    context = {}
    app_type = 'Направление'
    app_ref = 'hostelreferral'

    def render(self, obj_id):
        app = HostelReferral.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):

            hostel_address = 'пр. Н. Назарбаева 56/2'
            if app.room.hostel == 'Общежитие №3':
                hostel_address = 'ул. Терешкова 40'

            hostel = app.room.hostel
            room = "Комната " + str(app.room.number)

            first_date = app.appearance_start
            first_date = first_date.strftime("%d.%m.%Y")

            second_date = app.appearance_end
            second_date = second_date.strftime("%d.%m.%Y")

            appearance = first_date + " - " + second_date

            context = {
                'app': app,
                'address': hostel_address,
                'hostel': hostel,
                'room': room,
                'appearance': appearance,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=hostel_referral&id={obj_id}')
            }
            return render_pdf('applications/hostel_referral.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


@login_required
def get_notifications(request):
    """
    Получить все уведомления
    """
    notifications = Notification.objects.filter(is_showed=False).order_by('-date')
    notifications = serializers.serialize("json", notifications)
    data = json.loads(notifications)
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
                        'recovery': Recovery,
                        'hostel_referral': HostelReferral,
                        'academic_leave_return': AcademicLeaveReturn,
                        'private_information_change': PrivateInformationChange,
                        'expulsion': Expulsion,
                        'transfer-inside': TransferInside,
                        'key-card': KeyCard,
                        'reference-student': ReferenceStudent,
                        'key-card-first': KeyCardFirst}

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


def check_hostel(request):
    """
    Проверка
    заявления на общежитие
    """
    template_form = 'ssc/check_hostel_form.html'
    template_result = 'ssc/check_hostel_status.html'

    if request.method == 'POST':
        individual_identification_number = request.POST.get('iin')
        try:
            orders = Hostel.objects.filter(individual_identification_number=individual_identification_number).order_by(
                '-date_of_application')
            if orders.count() == 0:
                raise Hostel.DoesNotExist
            else:
                order = orders.first()

            status = ""
            if order.status == 'Не проверено':
                status = "Проверка"
            elif order.status == 'Отозвано на исправление':
                status = "Отозвано на исправление"
            else:
                referrals = HostelReferral.objects.filter(
                    individual_identification_number=individual_identification_number).order_by('-date_of_application')

                if referrals.count() > 0:
                    referral = referrals.first()
                else:
                    raise HostelReferral.DoesNotExist

                if referral.status == 'Не рассмотрено':
                    status = 'Ожидает решения'
                else:
                    status = referral.status
                    print(referral.status)

            context = {'last_name': order.last_name,
                       'first_name': order.first_name,
                       'patronymic': order.patronymic,
                       'individual_identification_number': order.individual_identification_number,
                       'date': order.date_of_application,
                       'status': status}

            return render(request, template_result, context)

        except Hostel.DoesNotExist:
            messages.info(request, 'Заявка не найдена! Проверьте правильность ввода ИИН!')
            return HttpResponseRedirect('/check_hostel')
    else:
        return render(request, template_form)


def hostel_space(request):
    """
    Проверка
    мест в общежитии
    """

    template = 'ssc/hostel_space.html'

    all_space = dict()
    free_space = dict()

    overall_space = 0
    overall_free_space = 0

    # TODO:
    # Этот код является хотфиксом в условиях ограничений
    # В будущем требуется либо раскоментировать закоментированный, а остальной удалить
    # Либо требуется полный рефакторинг

    for room in HostelRoom.objects.all():
        # if room.hostel in all_space.keys():
        #   all_space[room.hostel] += room.all_space
        #    free_space[room.hostel] += room.free_space
        # else:
        #   all_space[room.hostel] = room.all_space
        #   free_space[room.hostel] = room.free_space

        space_count = 1
        if room.all_space > 2:
            space_count = 2
        if room.all_space > 5:
            space_count = 3

        if room.hostel == 'Общежитие №3' and room.all_space == 4:
            space_count = 3

        if room.hostel == 'Общежитие «Студенттер үйi»' and room.all_space == 4:
            space_count = 3
        if room.hostel == 'Общежитие «Студенттер үйi»' and (
                room.number == 235 or room.number == 403 or room.number == 203):
            space_count = 2
        if room.hostel == 'Общежитие Жилищный комплекс «Армандастар Ордасы»' and room.all_space >= 3:
            space_count = 3
        if room.hostel == 'Общежитие Жилищный комплекс «Армандастар Ордасы»' and room.all_space == 2:
            space_count = 2
        if room.hostel == 'Общежитие №3' and room.number == 321:
            space_count = 4

        if room.hostel in all_space.keys():
            all_space[room.hostel] += space_count
            if room.all_space == room.free_space:
                free_space[room.hostel] += space_count
            if room.all_space - room.free_space == 1 and space_count == 2:
                free_space[room.hostel] += 1
            if room.all_space - room.free_space == 1 and space_count == 3:
                free_space[room.hostel] += 2
            if room.all_space - room.free_space == 2 and space_count == 3:
                free_space[room.hostel] += 1
            if space_count == 4:
                free_space[room.hostel] += room.free_space - 2
        else:
            all_space[room.hostel] = space_count
            free_space[room.hostel] = 0
            if room.all_space == room.free_space:
                free_space[room.hostel] = space_count
            if room.all_space - room.free_space == 1 and space_count == 2:
                free_space[room.hostel] = 1
            if room.all_space - room.free_space == 1 and space_count == 3:
                free_space[room.hostel] = 2
            if room.all_space - room.free_space == 2 and space_count == 3:
                free_space[room.hostel] = 1
            if space_count == 4:
                free_space[room.hostel] = room.free_space - 2

        # overall_space += room.all_space
        # overall_free_space += room.free_space
        overall_space += space_count
        if room.all_space == room.free_space:
            overall_free_space += space_count
        if room.all_space - room.free_space == 1 and space_count == 2:
            overall_free_space += 1
        if room.all_space - room.free_space == 1 and space_count == 3:
            overall_free_space += 2
        if room.all_space - room.free_space == 2 and space_count == 3:
            overall_free_space += 1

    time = timezone.localtime(timezone.now())
    time = time.strftime("%d/%m/%Y, %H:%M")

    result = []

    for hostel in all_space:
        result.append({'hostel': hostel,
                       'all_space': all_space[hostel],
                       'taken_space': all_space[hostel] - free_space[hostel],
                       'free_space': free_space[hostel]})

    result.append({'hostel': 'Итого',
                   'all_space': overall_space,
                   'taken_space': overall_space - overall_free_space,
                   'free_space': overall_free_space})

    context = {'result': result,
               'time': time}
    return render(request, template, context)


def hostel_referral_list(request):
    """
    Проверка
    списка назначенных направлений
    """
    template = 'ssc/hostel_referral_list.html'

    # TODO: REFACTOR THIS CODE
    count = 1

    hostel_three = []

    for referral in HostelReferral.objects.filter(Q(status='Одобрено') | Q(status='Заселен')).filter(
            room__hostel='Общежитие №3'):
        hostel_three.append({'count': count,
                             'full_name': referral.last_name + " " + referral.first_name + " " + referral.patronymic,
                             'faculty': referral.faculty,
                             'course': referral.course,
                             'group': referral.group,
                             'room_number': referral.room.number})
        count += 1

    if len(hostel_three) == 0:
        hostel_three.append({'count': "",
                             'full_name': "",
                             'faculty': "",
                             'course': "",
                             'group': "",
                             'room_number': ""})

    count = 1

    hostel_armandastar = []
    for referral in HostelReferral.objects.filter(Q(status='Одобрено') | Q(status='Заселен')).filter(
            room__hostel='Общежитие Жилищный комплекс «Армандастар Ордасы»'):
        hostel_armandastar.append({'count': count,
                                   'full_name': referral.last_name + " " + referral.first_name + " " + referral.patronymic,
                                   'faculty': referral.faculty,
                                   'course': referral.course,
                                   'group': referral.group,
                                   'room_number': referral.room.number})
        count += 1

    if len(hostel_armandastar) == 0:
        hostel_armandastar.append({'count': "",
                                   'full_name': "",
                                   'faculty': "",
                                   'course': "",
                                   'group': "",
                                   'room_number': ""})

    count = 1

    hostel_uyi = []
    for referral in HostelReferral.objects.filter(Q(status='Одобрено') | Q(status='Заселен')).filter(
            room__hostel='Общежитие «Студенттер үйi»'):
        hostel_uyi.append({'count': count,
                           'full_name': referral.last_name + " " + referral.first_name + " " + referral.patronymic,
                           'faculty': referral.faculty,
                           'course': referral.course,
                           'group': referral.group,
                           'room_number': referral.room.number})
        count += 1

    if len(hostel_uyi) == 0:
        hostel_uyi.append({'count': "",
                           'full_name': "",
                           'faculty': "",
                           'course': "",
                           'group': "",
                           'room_number': ""})

    context = {'hostel_three': hostel_three,
               'hostel_armandastar': hostel_armandastar,
               'hostel_uyi': hostel_uyi}
    return render(request, template, context)


class AcademicLeaveReturnView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Возвращение из академических отпусков обучающихся в организациях образования"
    Государственная услуга
    """
    form_class = AcademicLeaveReturnForm
    template_name = 'ssc/academic-leave-return.html'
    context = {'status': statuses.get('academic-leave-return')}
    app_type = 'Возвращение из акадического отпуска'
    app_ref = 'academicleavereturn'

    @login_required
    def render(self, obj_id):
        app = AcademicLeaveReturn.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):

            documents = {
                'по состоянию здоровья': 'Справка ВКК',
                'с призывом на воинскую службу': 'Копия военного билета',
                'с рождением ребенка': 'Копия свидетельства о рождении ребенка'
            }

            context = {
                'stuff_position': Stuff.objects.get(application_type='Возвращение из акадического отпуска').position,
                'stuff_name': Stuff.objects.get(application_type='Возвращение из акадического отпуска').name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=academic_leave_return&id={obj_id}'),
                'document': documents[app.reason]
            }
            return render_pdf('applications/academic-leave-return.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


class PrivateInformationChangeView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Изменение персональных данных об обучающихся в организациях образования"
    Государственная услуга
    """
    form_class = PrivateInformationChangeForm
    template_name = 'ssc/private-information-change.html'
    context = {'status': statuses.get('private-information-change')}
    app_type = 'Изменение персональных данных'
    app_ref = 'privateinformationchange'

    @login_required
    def render(self, obj_id):
        app = PrivateInformationChange.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'stuff_position': Stuff.objects.get(application_type='Изменение персональных данных').position,
                'stuff_name': Stuff.objects.get(application_type='Изменение персональных данных').name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=private_information_change&id={obj_id}')
            }
            return render_pdf('applications/private-information-change.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


class ExpulsionView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Отчисление обучающихся в организациях образования"
    Государственная услуга
    """
    form_class = ExpulsionForm
    template_name = 'ssc/expulsion.html'
    context = {'status': statuses.get('expulsion')}
    app_type = 'Отчисление'
    app_ref = 'expulsion'

    @login_required
    def render(self, obj_id):
        app = Expulsion.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'stuff_position': Stuff.objects.get(application_type='Отчисление').position,
                'stuff_name': Stuff.objects.get(application_type='Отчисление').name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=expulsion&id={obj_id}')
            }
            return render_pdf('applications/expulsion.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


class TransferInsideView(TemplateView):
    """
    Представления для подачи заявления по услуге
    "Перевод обучающихся внутри организации образования"
    Государственная услуга
    """
    form_class = TransferInsideForm
    template_name = 'ssc/transfer-inside.html'
    context = {'status': statuses.get('transfer-inside')}
    app_type = 'Перевод внутри ВУЗа'
    app_ref = 'transferinside'

    @login_required
    def render(self, obj_id):
        app = TransferInside.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'stuff_position': Stuff.objects.get(application_type='Перевод внутри ВУЗа').position,
                'stuff_name': Stuff.objects.get(application_type='Перевод внутри ВУЗа').name,
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=transfer-inside&id={obj_id}')
            }
            return render_pdf('applications/transfer-inside.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено!</h1></center>')


class KeyCardView(TemplateView):
    """
    Представления для подачи заявки по услуге
    "Восстановление ключ-карты в связи с утерей"
    """
    form_class = KeyCardForm
    template_name = 'ssc/key-card.html'
    context = {'status': statuses.get('key-card')}
    app_type = 'Восстановление ключ-карты'
    app_ref = 'keycard'

    @login_required
    def render(self, obj_id):
        app = KeyCard.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=key-card&id={obj_id}')
            }
            return render_pdf('applications/key-card.html', context)
        else:
            return HttpResponse('<center><h1>Заявка не потверждена!</h1></center>')


class ReferenceStudentView(TemplateView):
    """
    Представления для подачи заявки по услуге
    "Восстановление ключ-карты в связи с утерей"
    """
    form_class = ReferenceStudentForm
    template_name = 'ssc/reference-student.html'
    context = {'status': statuses.get('reference-student')}
    app_type = 'Выдача транскрипта обучающимся'
    app_ref = 'referencestudent'

    @login_required
    def render(self, obj_id):
        app = ReferenceStudent.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=reference-student&id={obj_id}')
            }
            return render_pdf('applications/reference-student.html', context)
        else:
            return HttpResponse('<center><h1>Заявка не потверждена!</h1></center>')


class KeyCardFirstView(TemplateView):
    """
    Представления для подачи заявки по услуге
    "Получение ключ-карты при переводе/восстановлении"
    """
    form_class = KeyCardFirstForm
    template_name = 'ssc/key-card-first.html'
    context = {'status': statuses.get('key-card-first')}
    app_type = 'Получение ключ-карты'
    app_ref = 'keycardfirst'

    @login_required
    def render(self, obj_id):
        app = KeyCardFirst.objects.get(id=obj_id)
        if app.status not in ('Не проверено', 'Отозвано на исправление'):
            context = {
                'app': app,
                'qr_code': generate_qr_code(f'{BASE_URL}/check_order?order_type=key-card-first&id={obj_id}')
            }
            return render_pdf('applications/key-card-first.html', context)
        else:
            return HttpResponse('<center><h1>Заявка не потверждена!</h1></center>')
