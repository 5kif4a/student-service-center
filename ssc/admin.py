from django.contrib import admin
from django.utils.html import format_html

from SSC_KSTU.settings import BASE_URL, DEBUG
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
                "reference": "[obj.iin_attachment_front.path, obj.iin_attachment_back.path]",

                "academic-leave": "[obj.iin_attachment_front.path, obj.iin_attachment_back.path, obj.attachment.path]",

                "abroad": "[obj.passport.path, obj.recommendation_letter.path, obj.transcript.path, "
                          "obj.certificate.path]",

                "hostel": "[obj.iin_attachment_front.path, obj.iin_attachment_back.path, obj.attachment.path]",

                "transfer": "[]",

                "transfer-kstu": "[obj.iin_attachment_front.path, obj.iin_attachment_back.path, "
                                 "obj.permission_to_transfer.path, obj.certificate.path, obj.transcript.path]",

                "recovery": "[obj.iin_attachment_front.path, obj.iin_attachment_back.path, obj.attachment.path, "
                            "obj.certificate.path] "
            }

            # UNSAFE CODE BEGIN
            filenames_as_str = filenames_dict.get(self.entity)
            filenames = eval(filenames_as_str)
            # UNSAFE CODE END
            response = make_zip_response(filenames)
            return response

        # Завершение обработки заявления
        if "_finish" in request.POST:
            # Если завершено - выдаем сообщение, что заявление уже завершено
            if obj.status is 'Завершено':
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
    service_name = "Выдача справки лицам, не завершившим высшее и послевузовское образование"
    app = 'Ваша справка готова. Вы можете получить ее в КарГТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'receipt_year', 'exclude_year', 'education_form', 'course', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number')
    autocomplete_fields = ('specialty',)

    readonly_fields = ('id_card_front', 'id_card_back')


@admin.register(AcademicLeave)
class AcademicLeaveAdmin(CustomAdmin):
    """
    Админ.панель академ.отпусков
    """
    entity = 'academic-leave'
    mail_template = 'mails/academic-leave.html'
    change_form_template = "custom_admin/academic-leave.html"
    # app = 'Ваш приказ готов. Вы можете получить его в КарГТУ, 1 корпус, кабинет № 109.'
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
            if obj.status is 'Завершено':
                self.message_user(request, f"{obj} обработка завершена")
            # Если не завершено - завершаем и отправляем письмо на почту
            else:
                obj.status = 'Завершено'
                obj.save()

                ctx = {'name': obj.first_name}
                to = (obj.email,)

                uploaded_file = request.FILES['scanned_file']
                send_email_with_attachment("mails/ready/academic-leave.html", ctx, to, uploaded_file)

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
    app = 'Ваша справка готова. Вы можете получить ее в КарГТУ, 1 корпус, кабинет № 109.'
    service_name = "Предоставление общежития обучающимся в высших учебных заведениях"
    list_per_page = 15
    list_filter = ('date_of_application', 'faculty', 'course', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number')
    autocomplete_fields = ('specialty',)
    readonly_fields = ('id_card_front', 'id_card_back')


# @admin.register(Duplicate)
# class DuplicateAdmin(CustomAdmin):
#     """
#     Админ.панель дубликатов
#     """
#     entity = 'duplicate'
#     app = 'Ваш дубликат готов. Вы можете получить его в КарГТУ, 1 корпус, кабинет № 109.'
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
    app = 'Ваше заявление подписано. Вы можете получить его в КарГТУ, 1 корпус, кабинет № 109.'
    service_name = "Перевод в друой ВУЗ"
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
    Админ.панель переводов в КарГТУ
    """
    entity = 'transfer-kstu'
    mail_template = 'mails/transfer-kstu.html'
    app = 'Ваше заявление принято. Вам необходимо в течение 1 дня подойти в КарГТУ, ' \
          'главный корпус, кабинет № 309 б., ' \
          'для заключения договора. При себе иметь удостоверение личности. ' \
          'После подписания договора подойти в каб. № 109, 1 корпус.'
    service_name = "Перевод в КарГТУ"
    list_per_page = 15
    list_filter = (
    'date_of_application', 'faculty', 'course', 'foundation_on_previous_university', 'foundation_in_kstu', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status', 'print')
    search_fields = ('last_name', 'first_name', 'patronymic', 'address',
                     'specialty__name', 'individual_identification_number', 'university')
    autocomplete_fields = ('specialty',)
    readonly_fields = ('id_card_front', 'id_card_back')


@admin.register(Recovery)
class RecoveryAdmin(CustomAdmin):
    """
    Админ.панель - восстановление в число обучающихся
    """
    entity = 'recovery'
    mail_template = 'mails/recovery.html'
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
