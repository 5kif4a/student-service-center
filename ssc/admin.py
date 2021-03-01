from django.contrib import admin
from django.db.models import Max
from django.utils.html import format_html
from rangefilter.filter import DateRangeFilter

from SSC_KSTU.settings import BASE_URL, DEBUG
from ssc.filters import CategoryFilter
from ssc.models import *
from ssc.utilities import *

# Заголовки админ.сайта
admin.site.index_title = 'Центр обслуживания студентов'
admin.site.site_header = 'Центр обслуживания студентов'
admin.site.site_title = 'Административная панель'

# кастомная главная страница админ.панели
admin.site.index_template = 'custom_admin/base_site.html'


# Метод получения всех полей модели(столбцов таблицы)
def get_model_fields(model):
    return [field.name for field in model._meta.get_fields()][1:]


# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Админ.панель для списка студентов
    """
    list_per_page = 30
    list_filter = ('education_form', 'language_department', 'degree', 'course', 'faculty', 'specialty',
                   'student_status')
    list_display = get_model_fields(Student)
    search_fields = get_model_fields(Student)


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    """
    Админ.панель для списка специальностей
    """
    list_per_page = 30
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    """
    Админ.панель для списка университетов
    """
    list_per_page = 30
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Rector)
class RectorAdmin(admin.ModelAdmin):
    """
    Админ.панель для списка ректоров
    """
    list_display = get_model_fields(Rector)


class CustomAdmin(admin.ModelAdmin):
    """
    Класс шаблон кастомной админ.панели для каждой услуги
    """
    mail_template = None
    change_form_template = "custom_admin/change_form.html"
    entity = None
    app = None
    ready_mail = "mails/ready/ready.html"
    service_name = None
    filenames = None

    def id_card_front(self, obj):
        return format_html(f"""<img src="{obj.iin_attachment_front.url}" width="300px">""")

    def id_card_back(self, obj):
        return format_html(f"""<img src="{obj.iin_attachment_back.url}" width="300px">""")

    id_card_front.short_description = "Уд.личности передняя сторона"
    id_card_back.short_description = "Уд.личности обратная сторона"

    def print(self, obj):
        url = f'/{self.entity}/report/{obj.id}'
        if obj.status in ('Подтверждено', 'Завершено'):
            button = f"""
                     <input type="button" class="button" value="Печать" onclick="window.open('{url}', '_blank')">
                     """
        else:
            # TODO - refactor this HTML code
            button = f"""
                    <input type="button" 
                    class="button" 
                    style="cursor: not-allowed; background-color: #DC3545" 
                    value="Печать"
                    onclick="window.open('{url}', '_blank')" 
                    disabled>
                    """

        return format_html(button)

    print.short_description = "Печать"

    def response_change(self, request, obj):
        # Если заявление заполнено неправильно, отправляем письмо с уведомлением
        if "_send_for_correction" in request.POST:
            if obj.status != 'Отозвано на исправление':
                note = request.POST.get('note')

                obj.status = 'Отозвано на исправление'
                obj.save()

                ctx = {'name': obj.first_name,
                       'note': note}
                to = (obj.email,)
                send_email('mails/revoke.html', ctx, to)
                self.message_user(request, f"Письмо с уведомлением отправлено {obj}")
            else:
                self.message_user(request, f"Письмо с уведомлением уже отправлено {obj}")

        # Потверждение заявления
        if "_verify" in request.POST:
            # Если подтвержден - выдаем сообщение, что заявление уже подтверждено
            if obj.status == 'Подтверждено':
                self.message_user(request, f"{obj} уже потвержден")
            # Если не потверждено - подтверждаем и отправляем письмо на почту
            else:
                obj.status = 'Подтверждено'
                obj.save()

                # отправляем письмо после потверждения заявления
                ctx = {'name': request.POST['first_name']}
                to = (request.POST.get('email', ''),)

                send_email(self.mail_template, ctx, to)

                self.message_user(request, f"""{obj} подтверждено""")

        # скачать архив с прикреплениями
        if "_download_zip" in request.POST:
            filenames_dict = {
                "reference": "[]",

                "academic-leave": "[obj.iin_attachment_front.path, obj.iin_attachment_back.path, obj.attachment.path]",

                "abroad": "[obj.passport.path, obj.recommendation_letter.path, obj.transcript.path, "
                          "obj.certificate.path]",

                "hostel": "[obj.iin_attachment_front.path, obj.iin_attachment_back.path, obj.attachmentProperty.path]",

                "transfer": "[]",

                "transfer-kstu": "[obj.iin_attachment_front.path, obj.iin_attachment_back.path, "
                                 "obj.permission_to_transfer.path, obj.certificate.path, obj.transcript.path]",

                "recovery": "[obj.iin_attachment_front.path, obj.iin_attachment_back.path, obj.attachment.path, "
                            "obj.certificate.path] ",

                "hostel_referral": "[obj.iin_attachment_front.path, obj.iin_attachment_back.path, obj.attachmentProperty.path]"
            }

            if obj.__class__ is Hostel or obj.__class__ is HostelReferral:
                if obj.attachmentDeath:
                    filenames_dict["hostel"] = filenames_dict["hostel"][0:-1] + ",obj.attachmentDeath.path]"
                    filenames_dict["hostel_referral"] = filenames_dict["hostel_referral"][0:-1] + \
                                                        ", obj.attachmentDeath.path]"
                if obj.attachmentLarge:
                    filenames_dict["hostel"] = filenames_dict["hostel"][0:-1] + ",obj.attachmentLarge.path]"
                    filenames_dict["hostel_referral"] = filenames_dict["hostel_referral"][0:-1] + \
                                                        ", obj.attachmentLarge.path]"
                if obj.attachmentDisabled:
                    filenames_dict["hostel"] = filenames_dict["hostel"][0:-1] + ",obj.attachmentDisabled.path]"
                    filenames_dict["hostel_referral"] = filenames_dict["hostel_referral"][0:-1] + \
                                                        ", obj.attachmentDisabled.path]"
                if obj.attachmentKandas:
                    filenames_dict["hostel"] = filenames_dict["hostel"][0:-1] + ",obj.attachmentKandas.path]"
                    filenames_dict["hostel_referral"] = filenames_dict["hostel_referral"][0:-1] + \
                                                        ", obj.attachmentKandas.path]"

            if obj.__class__ is AcademicLeave or obj.__class__ is Recovery:
                if not obj.attachment:
                    filenames_dict["academic-leave"] = "[obj.iin_attachment_front.path, obj.iin_attachment_back.path]"
                    filenames_dict["recovery"] = "[obj.iin_attachment_front.path, obj.iin_attachment_back.path, " \
                                                 "obj.certificate.path] "

            # UNSAFE CODE BEGIN
            filenames_as_str = filenames_dict.get(self.entity)
            filenames = eval(filenames_as_str)
            # UNSAFE CODE END
            if self.entity == "transfer-kstu":
                if obj.grant:
                    filenames.append(obj.grant.path)

            response = make_zip_response(filenames)
            return response

        # Завершение обработки заявления
        if "_finish" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status == 'Завершено':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:
                obj.status = 'Завершено'
                obj.save()

                ctx = {'name': obj.first_name,
                       'app': self.app,
                       'service_name': self.service_name
                       }
                to = (obj.email,)

                send_email(self.ready_mail, ctx, to)

                self.message_user(request, f"""Обработка заявления "{obj}" завершена. Письмо отправлено""")

        return super().response_change(request, obj)


@admin.register(Reference)
class ReferenceAdmin(CustomAdmin):
    """
    Админ.панель академ.справок
    """
    entity = 'reference'
    mail_template = 'mails/reference.html'
    service_name = "Выдача транскрипта"
    app = 'Ваш транскрипт готов. Вы можете получить его в КарТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'receipt_year', 'exclude_year', 'education_form', 'course', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number')
    autocomplete_fields = ('specialty',)


@admin.register(AcademicLeave)
class AcademicLeaveAdmin(CustomAdmin):
    """
    Админ.панель академ.отпусков
    """
    entity = 'academic-leave'
    mail_template = 'mails/academic-leave.html'
    mail_template_prolongation = 'mails/academic-leave-prolongation.html'
    change_form_template = "custom_admin/academic-leave.html"
    # app = 'Ваш приказ готов. Вы можете получить его в КарТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'status', 'is_prolongation')
    list_display = (
        'last_name', 'first_name', 'patronymic', 'specialty', 'is_prolongation', 'date_of_application', 'status',
        'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number', 'number')
    autocomplete_fields = ('specialty',)

    readonly_fields = ('attachment', 'id_card_front', 'id_card_back', 'leave_start', 'leave_end', 'number')

    def response_change(self, request, obj):
        # Если заявление заполнено неправильно, отправляем письмо с уведомлением
        if "_send_for_correction" in request.POST:
            if obj.status != 'Отозвано на исправление':
                note = request.POST.get('note')

                obj.status = 'Отозвано на исправление'
                obj.save()

                ctx = {'name': obj.first_name,
                       'note': note}
                to = (obj.email,)
                send_email('mails/revoke.html', ctx, to)
                self.message_user(request, f"Письмо с уведомлением отправлено {obj}")
            else:
                self.message_user(request, f"Письмо с уведомлением уже отправлено {obj}")

        # Потверждение заявления
        if "_verify" in request.POST:
            # Если подтвержден - выдаем сообщение, что заявление уже подтверждено
            if obj.status == 'Подтверждено':
                self.message_user(request, f"{obj} уже потвержден")
            # Если не потверждено - подтверждаем и отправляем письмо на почту
            else:
                obj.status = 'Подтверждено'
                obj.save()

                # отправляем письмо после потверждения заявления
                ctx = {'name': request.POST['first_name']}
                to = (request.POST.get('email', ''),)

                if not obj.is_prolongation:
                    send_email(self.mail_template, ctx, to)
                else:
                    send_email(self.mail_template_prolongation, ctx, to)

                self.message_user(request, f"""{obj} подтверждено""")

        # Завершение обработки заявления
        if "_finish" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status == 'Завершено':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:
                obj.status = 'Завершено'

                obj.leave_start = request.POST['leave_start']
                obj.leave_end = request.POST['leave_end']
                obj.number = request.POST['number']
                obj.save()

                ctx = {'name': obj.first_name, 'number': obj.number, 'date_start': obj.leave_start,
                       'date_end': obj.leave_end}
                to = (obj.email,)

                if not obj.is_prolongation:
                    send_email("mails/ready/academic-leave.html", ctx, to)
                else:
                    send_email("mails/ready/academic-leave-prolongation.html", ctx, to)

                self.message_user(request, f"""Обработка заявления "{obj}" завершена. Письмо отправлено""")

        return super().response_change(request, obj)


@admin.register(Abroad)
class AbroadAdmin(CustomAdmin):
    """
    Админ.панель академ.мобильности
    """
    entity = 'abroad'
    mail_template = 'mails/abroad.html'
    ready_mail = "mails/ready/abroad.html"
    app = 'Ваши документы для участия в конкурсе на обучение за рубежом, в том числе в рамках академической ' \
          'мобильности приняты.'
    list_per_page = 15
    list_filter = ('date_of_application', 'course', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status',
                    'print')
    search_fields = ('last_name', 'first_name', 'patronymic',
                     'individual_identification_number')

    # autocomplete_fields = ('university',)

    # readonly_fields = ('id_card_front', 'id_card_back')


@admin.register(Hostel)
class HostelAdmin(CustomAdmin):
    """
    Админ.панель предоставления общежития
    """
    entity = 'hostel'
    mail_template = 'mails/hostel.html'
    app = 'Ваше заявление принято в работу.'
    service_name = "Предоставление общежития обучающимся в высших учебных заведениях"
    list_per_page = 15
    list_filter = (('date_of_application', DateRangeFilter), 'faculty', 'course', 'status', CategoryFilter)
    list_display = (
        'last_name', 'first_name', 'patronymic', 'faculty', 'specialty', 'course', 'date_of_application', 'status',
        'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'specialty__name',
                     'individual_identification_number')
    autocomplete_fields = ('specialty',)
    readonly_fields = ('id_card_front', 'id_card_back', 'message')

    def response_change(self, request, obj):
        if "_send_for_correction" in request.POST:
            if obj.status != 'Отозвано на исправление':
                note = request.POST.get('note')

                obj.status = 'Отозвано на исправление'
                obj.message = note
                obj.save()

                ctx = {'name': obj.first_name,
                       'note': note}
                to = (obj.email,)
                send_email('mails/revoke.html', ctx, to)
                self.message_user(request, f"Письмо с уведомлением отправлено {obj}")
            else:
                self.message_user(request, f"Письмо с уведомлением уже отправлено {obj}")

        if "_verify" in request.POST:
            # Если подтвержден - выдаем сообщение, что заявление уже подтверждено
            if obj.status == 'Подтверждено':
                self.message_user(request, f"{obj} уже потвержден")
            # Если не потверждено - подтверждаем и отправляем письмо на почту
            else:
                referral = HostelReferral(last_name=obj.last_name, first_name=obj.first_name, patronymic=obj.patronymic,
                                          individual_identification_number=obj.individual_identification_number,
                                          email=obj.email, phone_number=obj.phone_number,
                                          course=obj.course, is_serpin=obj.is_serpin,
                                          group=obj.group, date_of_application=datetime.now(), faculty=obj.faculty,
                                          iin_attachment_front=obj.iin_attachment_front,
                                          iin_attachment_back=obj.iin_attachment_back,
                                          attachmentProperty=obj.attachmentProperty,
                                          attachmentDeath=obj.attachmentDeath,
                                          attachmentLarge=obj.attachmentLarge,
                                          attachmentDisabled=obj.attachmentDisabled,
                                          attachmentKandas=obj.attachmentKandas, specialty_id=obj.specialty_id)
                referral.save(True)

                obj.status = 'Подтверждено'
                obj.save()

                # отправляем письмо после потверждения заявления
                ctx = {'name': request.POST['first_name']}
                to = (request.POST.get('email', ''),)

                send_email(self.mail_template, ctx, to)

                self.message_user(request, f"""{obj} подтверждено""")

        if "_finish" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status == 'Завершено':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:

                obj.status = 'Завершено'
                obj.save()

                ctx = {'name': obj.first_name}
                to = (obj.email,)

                # uploaded_file = request.FILES['scanned_file']
                # send_email_with_attachment("mails/ready/academic-leave.html", ctx, to, uploaded_file)
                # send_email("mails/ready/academic-leave.html", ctx, to)

                self.message_user(request, f"""Обработка заявления "{obj}" завершена. Письмо отправлено""")

        return super().response_change(request, obj)


# @admin.register(Duplicate)
# class DuplicateAdmin(CustomAdmin):
#     """
#     Админ.панель дубликатов
#     """
#     entity = 'duplicate'
#     app = 'Ваш дубликат готов. Вы можете получить его в КарТУ, 1 корпус, кабинет № 109.'
#     list_per_page = 15
#     list_filter = ('date_of_application', 'reason', 'duplicate_type', 'status')
#     list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status', 'print')
#     readonly_fields = ('id_card',)
#     search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
#                      'individual_identification_number')
#
#     def id_card(self, obj):
#         return format_html(f"""<img src="{obj.iin_attachment.url}" width="300px">""")


@admin.register(Transfer)
class TransferAdmin(CustomAdmin):
    """
    Админ.панель переводов в другой ВУЗ
    """
    entity = 'transfer'
    mail_template = 'mails/transfer.html'
    app = 'Ваше заявление подписано. Вы можете получить его в КарТУ, 1 корпус, кабинет № 109.'
    service_name = "Перевод в другой ВУЗ"
    list_per_page = 15
    list_filter = ('date_of_application', 'faculty', 'foundation_in_kstu', 'foundation_in_transfer', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status', 'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'current_specialty__name',
                     'individual_identification_number', 'university', 'group')
    autocomplete_fields = ('current_specialty', 'specialty')
    # readonly_fields = ('id_card_front', 'id_card_back')


@admin.register(TransferKSTU)
class TransferKSTUAdmin(CustomAdmin):
    """
    Админ.панель переводов в КарТУ
    """
    entity = 'transfer-kstu'
    mail_template = 'mails/transfer-kstu.html'
    ready_mail = 'mails/ready/transfer-kstu.html'
    app = 'Ваше заявление принято. Вам необходимо в течение 1 дня подойти в КарТУ, ' \
          'главный корпус, кабинет № 309 б., ' \
          'для заключения договора. При себе иметь удостоверение личности. ' \
          'После подписания договора подойти в каб. № 109, 1 корпус.'
    service_name = "Перевод в КарТУ"
    list_per_page = 15
    list_filter = (
        'date_of_application', 'faculty', 'course', 'foundation_on_previous_university', 'foundation_in_kstu', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status', 'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address',
                     'specialty_on_previous_university__name', 'transfer_specialty__name',
                     'individual_identification_number', 'university')
    autocomplete_fields = ('specialty_on_previous_university', 'transfer_specialty')
    readonly_fields = ('id_card_front', 'id_card_back')


@admin.register(Recovery)
class RecoveryAdmin(CustomAdmin):
    """
    Админ.панель - восстановление в число обучающихся
    """
    entity = 'recovery'
    mail_template = 'mails/recovery.html'
    ready_mail = 'mails/ready/recovery.html'
    app = 'Ваше заявление принято.'
    service_name = "Восстановление в число обучающихся"
    list_per_page = 15
    list_filter = ('date_of_application', 'faculty', 'course', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status', 'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number', 'university')
    autocomplete_fields = ('specialty',)
    readonly_fields = ('id_card_front', 'id_card_back')


# Уведомления
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Админ.панель для управления уведомлениями
    """

    def make_read(self, request, queryset):
        queryset.update(is_showed=True)

    make_read.short_description = "Отметить прочитанными выделенные уведомления"

    list_per_page = 20
    list_filter = ('application_type',)
    list_display = ('application_type', 'date', 'is_showed', 'link', 'mark_as_read')
    fields = ('application_type', 'is_showed')
    exclude = ('url_for_application',)
    readonly_fields = ('application_type', 'url_for_application', 'is_showed')
    actions = (make_read,)

    def mark_as_read(self, obj):
        """
        Кнопка в админ.панели, которая помечает уведомление как прочитанное
        :param obj: объект - уведомление
        :return: HTML
        """
        url = f'/mark_as_read/{obj.id}'
        protocol = 'http' if DEBUG else 'https'

        # можно было сделать как в CustomAdmin
        func = "fetch('{}://{}{}')".format(protocol, BASE_URL, url)

        if obj.is_showed:
            button = f"""<input 
                         type="button" 
                         class="button" 
                         style="cursor: not-allowed; background-color: #DC3545" 
                         value="Отметить как прочитанное" 
                         disabled>"""
        else:
            button = f'<input type="submit" class="button" value="Отметить как прочитанное" onclick="{func}">'

        return format_html(button)

    def link(self, obj):
        """
        Ссылка на заявление
        :param obj: Объект - уведомление
        :return: HTML
        """
        url = ''
        full_url = obj.url_for_application
        if full_url.startswith(BASE_URL):
            url = full_url[len(BASE_URL):]

        link = f'<a href="{url}" target="_blank">Перейти к заявлению</a>'

        return format_html(link)

    def has_add_permission(self, request):
        return False

    link.short_description = "Заявление"
    mark_as_read.short_description = "Отметить как прочитанное"


@admin.register(HostelRoom)
class HostelRoomAdmin(admin.ModelAdmin):
    """
    Админ.панель для списка свободных мест
    """
    list_display = ('number', 'hostel', 'sex', 'all_space', 'free_space')
    list_per_page = 15
    list_filter = ('hostel', 'free_space', 'sex')
    search_fields = ('number', 'hostel', 'free_space', 'sex')

    def changeform_view(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            self.readonly_fields = ('number', 'hostel', 'all_space', 'free_space')
        return super(HostelRoomAdmin, self).changeform_view(request, *args, **kwargs)


@admin.register(HostelReferral)
class HostelReferralAdmin(CustomAdmin):
    """
    Админ.панель для направления в общежитие
    """
    entity = 'hostel_referral'
    mail_template = 'mails/hostel_referral.html'
    change_form_template = "custom_admin/hostel_referral.html"
    app = 'Ваше направление в общежитие готово.'
    service_name = "Предоставление общежития обучающимся в высших учебных заведениях"
    list_per_page = 15
    list_filter = (
        ('date_of_application', DateRangeFilter), ('date_of_referral', DateRangeFilter),
        ('date_of_evict', DateRangeFilter),
        'is_serpin', 'room__hostel', 'faculty', 'course', 'status',
        CategoryFilter, 'is_registered')
    list_display = (
        'last_name', 'first_name', 'patronymic', 'individual_identification_number', 'faculty', 'course',
        'date_of_application',
        'status',
        'room', 'is_registered', 'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'specialty__name',
                     'individual_identification_number', 'room__number', 'room__hostel')
    autocomplete_fields = ('specialty', 'room')
    readonly_fields = (
        'id_card_front', 'id_card_back', 'number', 'message', 'appearance_start', 'appearance_end', 'date_of_referral',
        'date_of_evict')

    def response_change(self, request, obj):

        # Если в предоставлении общежития отказано отправляем уведомление
        if "_refuse" in request.POST:
            if obj.status != 'Отказано':
                note = request.POST.get('note')

                if obj.status == 'Одобрено':
                    obj.room.free_space += 1
                    obj.room.save()
                    obj.room = None

                obj.status = 'Отказано'
                obj.message = note
                obj.save()

                ctx = {'name': obj.first_name,
                       'note': note}
                to = (obj.email,)
                send_email('mails/hostel_refuse.html', ctx, to)
                self.message_user(request, f"Письмо с уведомлением отправлено {obj}")
            else:
                self.message_user(request, f"Письмо с уведомлением уже отправлено {obj}")

        # Потверждение заявления
        if "_approve" in request.POST:
            # Если подтвержден - выдаем сообщение, что заявление уже подтверждено
            if obj.status == 'Одобрено':
                self.message_user(request, f"{obj} уже потвержден")
            # Если не потверждено - подтверждаем и отправляем письмо на почту
            else:
                obj.status = 'Одобрено'

                appearance_first = request.POST.get('verify_first')
                appearance_last = request.POST.get('verify_second')

                try:
                    referral_number = HostelReferral.objects.all().aggregate(Max('number'))
                    referral_number = referral_number['number__max'] + 1
                except:
                    referral_number = 10001

                obj.number = referral_number

                obj.appearance_start = appearance_first
                obj.appearance_end = appearance_last

                obj.room.free_space -= 1
                obj.room.save()

                obj.date_of_referral = datetime.now()
                obj.save()

                # отправляем письмо после потверждения заявления
                ctx = {'name': request.POST['first_name'],
                       'referral_url': f'https://{BASE_URL}/{self.entity}/report/{obj.id}'}
                to = (request.POST.get('email', ''),)

                # uploaded_file = request.FILES['scanned_file']
                # send_email_with_attachment("mails/ready/hostel_referral.html", ctx, to, uploaded_file)
                send_email("mails/hostel_referral.html", ctx, to)

                self.message_user(request, f"""{obj} подтверждено""")

        if "_populate" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status == 'Заселен':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:
                if obj.status != 'Одобрено':
                    if obj.room.free_space > 0:
                        obj.room.free_space -= 1
                    obj.room.save()

                obj.status = 'Заселен'
                obj.save()

                ctx = {'name': obj.first_name,
                       'room': obj.room}
                to = (obj.email,)

                send_email("mails/ready/hostel_referral.html", ctx, to)

                self.message_user(request, f"""Обработка заявления "{obj}" завершена. Письмо отправлено""")

        if "_evict" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status == 'Выселен':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:
                note = request.POST.get('evict-note')

                obj.status = 'Выселен'

                if obj.room.free_space < obj.room.all_space:
                    obj.room.free_space += 1
                obj.room.save()

                obj.room = None

                obj.date_of_evict = datetime.now()
                obj.message = note
                obj.save()

                ctx = {'name': obj.first_name,
                       'note': note}
                to = (obj.email,)

                send_email("mails/ready/hostel_referral_evict.html", ctx, to)

                self.message_user(request, f"""Обработка заявления "{obj}" завершена. Письмо отправлено""")

        if "_absence" in request.POST:
            if obj.status != 'Неявка':
                note = 'Неявка'

                if obj.status == 'Одобрено':
                    obj.room.free_space += 1
                    obj.room.save()
                    obj.room = None

                obj.status = 'Неявка'
                obj.message = note
                obj.save()

                ctx = {'name': obj.first_name,
                       'note': note}
                to = (obj.email,)
                send_email('mails/hostel_refuse.html', ctx, to)
                self.message_user(request, f"Письмо с уведомлением отправлено {obj}")
            else:
                self.message_user(request, f"Письмо с уведомлением уже отправлено {obj}")

        return super().response_change(request, obj)

    def print(self, obj):
        url = f'/{self.entity}/report/{obj.id}'
        if obj.status in ('Одобрено', 'Заселен', 'Выселен'):
            button = f"""
                     <input type="button" class="button" value="Печать" onclick="window.open('{url}', '_blank')">
                     """
        else:
            # TODO - refactor this HTML code
            button = f"""
                    <input type="button" 
                    class="button" 
                    style="cursor: not-allowed; background-color: #DC3545" 
                    value="Печать"
                    onclick="window.open('{url}', '_blank')" 
                    disabled>
                    """

        return format_html(button)

    print.short_description = "Печать"

    def populate_evict(self, obj):
        url = f'/admin/ssc/hostelreferral/{obj.id}/change/'
        if obj.status == 'Одобрено':
            button = f"""
                        <input type="button" class="button" value="Заселить" 
                        onclick="document.body.innerHTML += '<form id=postPopulate action={url} method=post><input type=hidden name=_populate value=_populate></form>';
document.getElementById('postPopulate').submit();">
                     """
        else:
            # TODO - refactor this HTML code
            button = f"""
                    <input type="button" 
                    class="button" 
                    style="cursor: not-allowed; background-color: #DC3545" 
                    value=""
                    onclick="window.open('{url}', '_blank')" 
                    disabled>
                    """

        return format_html(button)

    populate_evict.short_description = "Заселить/Выселить"

    obj_formfield = None

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.obj_formfield = obj
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            if self.obj_formfield is not None:
                if self.obj_formfield.room:
                    kwargs["queryset"] = HostelRoom.objects.filter(id=self.obj_formfield.room.id)
                else:
                    kwargs["queryset"] = HostelRoom.objects.filter(free_space__gt=0)

            else:
                kwargs["queryset"] = HostelRoom.objects.filter(free_space__gt=0)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(AcademicLeaveReturn)
class AcademicLeaveReturnAdmin(CustomAdmin):
    """
    Админ.панель вовзращения из академ.отпусков
    """
    entity = 'academic-leave-return'
    mail_template = 'mails/academic-leave-return.html'
    change_form_template = "custom_admin/academic-leave-return.html"
    # app = 'Ваш приказ готов. Вы можете получить его в КарТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number')
    autocomplete_fields = ('specialty',)

    readonly_fields = ('attachment', 'id_card_front', 'id_card_back', 'leave_end', 'number')

    def response_change(self, request, obj):
        # Если заявление заполнено неправильно, отправляем письмо с уведомлением
        if "_send_for_correction" in request.POST:
            if obj.status != 'Отозвано на исправление':
                note = request.POST.get('note')

                obj.status = 'Отозвано на исправление'
                obj.save()

                ctx = {'name': obj.first_name,
                       'note': note}
                to = (obj.email,)
                send_email('mails/revoke.html', ctx, to)
                self.message_user(request, f"Письмо с уведомлением отправлено {obj}")
            else:
                self.message_user(request, f"Письмо с уведомлением уже отправлено {obj}")

        # Потверждение заявления
        if "_verify" in request.POST:
            # Если подтвержден - выдаем сообщение, что заявление уже подтверждено
            if obj.status == 'Подтверждено':
                self.message_user(request, f"{obj} уже потвержден")
            # Если не потверждено - подтверждаем и отправляем письмо на почту
            else:
                obj.status = 'Подтверждено'
                obj.save()

                # отправляем письмо после потверждения заявления
                ctx = {'name': request.POST['first_name']}
                to = (request.POST.get('email', ''),)

                send_email(self.mail_template, ctx, to)

                self.message_user(request, f"""{obj} подтверждено""")

        # Завершение обработки заявления
        if "_finish" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status == 'Завершено':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:
                obj.status = 'Завершено'

                obj.leave_end = request.POST['leave_end']
                obj.number = request.POST['number']
                obj.save()

                date = datetime.strptime(obj.leave_end, '%Y-%m-%d')

                ctx = {'name': obj.first_name, 'number': obj.number, 'date': date.strftime("%d.%m.%Y")}
                to = (obj.email,)

                send_email("mails/ready/academic-leave-return.html", ctx, to)

                self.message_user(request, f"""Обработка заявления "{obj}" завершена. Письмо отправлено""")

        return super().response_change(request, obj)


@admin.register(PrivateInformationChange)
class PrivateInformationChangeAdmin(CustomAdmin):
    """
    Админ.панель смены персональных данных
    """
    entity = 'private-information-change'
    mail_template = 'mails/private-information-change.html'
    change_form_template = "custom_admin/change_form.html"
    # app = 'Ваш приказ готов. Вы можете получить его в КарТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number')
    autocomplete_fields = ('specialty',)

    readonly_fields = ('attachment', 'id_card_front', 'id_card_back')

    def response_change(self, request, obj):
        # Если заявление заполнено неправильно, отправляем письмо с уведомлением
        if "_send_for_correction" in request.POST:
            if obj.status != 'Отозвано на исправление':
                note = request.POST.get('note')

                obj.status = 'Отозвано на исправление'
                obj.save()

                ctx = {'name': obj.first_name,
                       'note': note}
                to = (obj.email,)
                send_email('mails/revoke.html', ctx, to)
                self.message_user(request, f"Письмо с уведомлением отправлено {obj}")
            else:
                self.message_user(request, f"Письмо с уведомлением уже отправлено {obj}")

        # Потверждение заявления
        if "_verify" in request.POST:
            # Если подтвержден - выдаем сообщение, что заявление уже подтверждено
            if obj.status == 'Подтверждено':
                self.message_user(request, f"{obj} уже потвержден")
            # Если не потверждено - подтверждаем и отправляем письмо на почту
            else:
                obj.status = 'Подтверждено'
                obj.save()

                # отправляем письмо после потверждения заявления
                ctx = {'name': request.POST['first_name']}
                to = (request.POST.get('email', ''),)

                send_email(self.mail_template, ctx, to)

                self.message_user(request, f"""{obj} подтверждено""")

        # Завершение обработки заявления
        if "_finish" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status == 'Завершено':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:
                obj.status = 'Завершено'
                obj.save()

                ctx = {'name': obj.first_name, }
                to = (obj.email,)

                send_email("mails/ready/private-information-change.html", ctx, to)

                self.message_user(request, f"""Обработка заявления "{obj}" завершена. Письмо отправлено""")

        return super().response_change(request, obj)


@admin.register(Expulsion)
class ExpulsionAdmin(CustomAdmin):
    """
    Админ.панель смены персональных данных
    """
    entity = 'expulsion'
    mail_template = 'mails/expulsion.html'
    change_form_template = "custom_admin/change_form.html"
    # app = 'Ваш приказ готов. Вы можете получить его в КарТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number')
    autocomplete_fields = ('specialty',)

    def response_change(self, request, obj):
        # Если заявление заполнено неправильно, отправляем письмо с уведомлением
        if "_send_for_correction" in request.POST:
            if obj.status != 'Отозвано на исправление':
                note = request.POST.get('note')

                obj.status = 'Отозвано на исправление'
                obj.save()

                ctx = {'name': obj.first_name,
                       'note': note}
                to = (obj.email,)
                send_email('mails/revoke.html', ctx, to)
                self.message_user(request, f"Письмо с уведомлением отправлено {obj}")
            else:
                self.message_user(request, f"Письмо с уведомлением уже отправлено {obj}")

        # Потверждение заявления
        if "_verify" in request.POST:
            # Если подтвержден - выдаем сообщение, что заявление уже подтверждено
            if obj.status == 'Подтверждено':
                self.message_user(request, f"{obj} уже потвержден")
            # Если не потверждено - подтверждаем и отправляем письмо на почту
            else:
                obj.status = 'Подтверждено'
                obj.save()

                # отправляем письмо после потверждения заявления
                ctx = {'name': request.POST['first_name']}
                to = (request.POST.get('email', ''),)

                send_email(self.mail_template, ctx, to)

                self.message_user(request, f"""{obj} подтверждено""")

        # Завершение обработки заявления
        if "_finish" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status == 'Завершено':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:
                obj.status = 'Завершено'
                obj.save()

                ctx = {'name': obj.first_name, }
                to = (obj.email,)

                send_email("mails/ready/expulsion.html", ctx, to)

                self.message_user(request, f"""Обработка заявления "{obj}" завершена. Письмо отправлено""")

        return super().response_change(request, obj)


@admin.register(TransferInside)
class TransferInsideAdmin(CustomAdmin):
    """
    Админ.панель перевода внутри ВУЗа
    """
    entity = 'transfer-inside'
    mail_template = 'mails/transfer-inside.html'
    change_form_template = "custom_admin/change_form.html"
    # app = 'Ваш приказ готов. Вы можете получить его в КарТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number')
    autocomplete_fields = ('specialty',)

    def response_change(self, request, obj):
        # Если заявление заполнено неправильно, отправляем письмо с уведомлением
        if "_send_for_correction" in request.POST:
            if obj.status != 'Отозвано на исправление':
                note = request.POST.get('note')

                obj.status = 'Отозвано на исправление'
                obj.save()

                ctx = {'name': obj.first_name,
                       'note': note}
                to = (obj.email,)
                send_email('mails/revoke.html', ctx, to)
                self.message_user(request, f"Письмо с уведомлением отправлено {obj}")
            else:
                self.message_user(request, f"Письмо с уведомлением уже отправлено {obj}")

        # Потверждение заявления
        if "_verify" in request.POST:
            # Если подтвержден - выдаем сообщение, что заявление уже подтверждено
            if obj.status == 'Подтверждено':
                self.message_user(request, f"{obj} уже потвержден")
            # Если не потверждено - подтверждаем и отправляем письмо на почту
            else:
                obj.status = 'Подтверждено'
                obj.save()

                # отправляем письмо после потверждения заявления
                ctx = {'name': request.POST['first_name']}
                to = (request.POST.get('email', ''),)

                send_email(self.mail_template, ctx, to)

                self.message_user(request, f"""{obj} подтверждено""")

        # Завершение обработки заявления
        if "_finish" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status == 'Завершено':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:
                obj.status = 'Завершено'
                obj.save()

                ctx = {'name': obj.first_name, }
                to = (obj.email,)

                send_email("mails/ready/transfer-inside.html", ctx, to)

                self.message_user(request, f"""Обработка заявления "{obj}" завершена. Письмо отправлено""")

        return super().response_change(request, obj)


@admin.register(KeyCard)
class KeyCardAdmin(CustomAdmin):
    """
    Админ.панель восстановление ключ-карты
    """
    entity = 'key-card'
    mail_template = 'mails/key-card.html'
    change_form_template = "custom_admin/change_form.html"
    # app = 'Ваш приказ готов. Вы можете получить его в КарТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status',
                    'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address',
                     'individual_identification_number')

    def response_change(self, request, obj):
        # Завершение обработки заявления
        if "_finish" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status == 'Завершено':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:
                obj.status = 'Завершено'
                obj.save()

                ctx = {'name': obj.first_name, }
                to = (obj.email,)

                send_email("mails/ready/key-card.html", ctx, to)

                self.message_user(request, f"""Обработка заявки "{obj}" завершена. Письмо отправлено""")

        return super().response_change(request, obj)


@admin.register(ReferenceStudent)
class ReferenceStudentAdmin(CustomAdmin):
    """
    Админ.панель выдачи транскриптов обучающимся
    """
    entity = 'reference-student'
    mail_template = 'mails/reference-student.html'
    change_form_template = "custom_admin/change_form.html"
    # app = 'Ваш приказ готов. Вы можете получить его в КарТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'status', 'is_signed')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status',
                    'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address',
                     'individual_identification_number')

    def response_change(self, request, obj):
        # Завершение обработки заявления
        if "_finish" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status == 'Завершено':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:
                obj.status = 'Завершено'
                obj.save()

                ctx = {'name': obj.first_name, }
                to = (obj.email,)

                send_email("mails/ready/reference-student.html", ctx, to)

                self.message_user(request, f"""Обработка заявки "{obj}" завершена. Письмо отправлено""")

        return super().response_change(request, obj)
