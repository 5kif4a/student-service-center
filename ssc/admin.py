from django.utils.html import format_html
from ssc.models import *
from ssc.views import stats
from ssc.utilities import *
from django.contrib import admin
from django.urls import path


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
    change_form_template = "custom_admin/change_form.html"
    entity = None
    app = None

    def print(self, obj):
        url = f'/{self.entity}/report/{obj.id}'
        if obj.status == 'Подтверждено':
            button = f"""
                     <input type="button" class="button" value="Печать" onclick="window.open('{url}', '_blank')">
                     """
        else:
            button = f"""
                    <input type="button" class="button" value="Печать" onclick="window.open('{url}', '_blank') disabled">
                     """
        return format_html(button)

    def response_change(self, request, obj):
        # Потверждение заявления
        if "_verify" in request.POST:
            # Если потвержден - выдаем сообщение, что заявление уже потверждено
            if obj.status in 'Потверждено':
                self.message_user(request, f"{obj} уже потвержден")
            # Если не потверждено - потверждаем и отправляем письмо на почту
            else:
                obj.status = 'Подтверждено'
                obj.save()

                ctx = {'name': obj.first_name,
                       'app': self.app}
                to = (obj.email,)

                send_email('mails/ready.html', ctx, to)
                self.message_user(request, f"""Заявление "{obj}" потверждено""")
            # return HttpResponseRedirect(".")
        # Если заявление заполнено неправильно, отправляем письмо с уведомлением
        if "_send_for_correction" in request.POST:
            if obj.status is not 'Отозвано на исправление':
                note = request.POST.get('note')
                to = (obj.email,)
                ctx = {'name': obj.first_name,
                       'note': note}
                obj.status = 'Отозвано на исправление'
                obj.save()

                send_email('mails/revoke.html', ctx, to)
                self.message_user(request, f"Письмо с уведомлением отправлено {obj}")
            else:
                self.message_user(request, f"Письмо с уведомлением уже отправлено {obj}")
        return super().response_change(request, obj)


@admin.register(Reference)
class ReferenceAdmin(CustomAdmin):
    """
    Админ.панель академ.справок
    """
    entity = 'reference'
    app = 'Ваша справка готова. Вы можете получить ее в КарГТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'receipt_year', 'exclude_year', 'education_form', 'course', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    readonly_fields = ('id_card',)
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number')

    def id_card(self, obj):
        return format_html(f"""<img src="{obj.iin_attachment.url}" width="300px">""")


@admin.register(AcademicLeave)
class AcademicLeaveAdmin(CustomAdmin):
    """
    Админ.панель академ.отпусков
    """
    entity = 'academic-leave'
    app = 'Ваш приказ готов. Вы можете получить его в КарГТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    readonly_fields = ('attachment',)
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number')


@admin.register(Abroad)
class AbroadAdmin(CustomAdmin):
    """
    Админ.панель академ.мобильности
    """
    entity = 'abroad'
    # TODO: текст от международного отдела
    app = ''
    list_per_page = 15
    list_filter = ('date_of_application', 'course', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status',
                    'print')
    readonly_fields = ('id_card',)
    search_fields = ('last_name', 'first_name', 'patronymic', 'address',
                     'individual_identification_number')

    def id_card(self, obj):
        return format_html(f"""<img src="{obj.iin_attachment.url}" width="300px">""")


@admin.register(Hostel)
class HostelAdmin(CustomAdmin):
    """
    Админ.панель предоставления общежития
    """
    entity = 'hostel'
    app = 'Ваша справка готова. Вы можете получить ее в КарГТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'faculty', 'course', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    readonly_fields = ('id_card',)
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number')

    def id_card(self, obj):
        return format_html(f"""<img src="{obj.iin_attachment.url}" width="300px">""")


@admin.register(Duplicate)
class DuplicateAdmin(CustomAdmin):
    """
    Админ.панель дубликатов
    """
    entity = 'duplicate'
    app = 'Ваш дубликат готов. Вы можете получить его в КарГТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'reason', 'duplicate_type', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status', 'print')
    readonly_fields = ('id_card',)
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number')

    def id_card(self, obj):
        return format_html(f"""<img src="{obj.iin_attachment.url}" width="300px">""")


@admin.register(Transfer)
class TransferAdmin(CustomAdmin):
    """
    Админ.панель переводов в другой ВУЗ
    """
    entity = 'transfer'
    app = 'Ваше заявление подписано. Вы можете получить его в КарГТУ, 1 корпус, кабинет № 109.'
    list_per_page = 15
    list_filter = ('date_of_application', 'faculty', 'foundation', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status', 'print')
    readonly_fields = ('id_card',)
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'current_specialty__name',
                     'specialty__name', 'individual_identification_number', 'university', 'group')

    def id_card(self, obj):
        return format_html(f"""<img src="{obj.iin_attachment.url}" width="300px">""")


@admin.register(TransferKSTU)
class TransferKSTUAdmin(CustomAdmin):
    """
    Админ.панель переводов в КарГТУ
    """
    entity = 'transfer-kstu'
    app = 'Ваше заявление принято. Вам необходимо в течение 1 дня подойти в КарГТУ, ' \
          'главный корпус, кабинет № 309 б., ' \
          'для заключения договора. При себе иметь удостоверение личности. ' \
          'После подписания договора подойти в каб. № 109, 1 корпус.'
    list_per_page = 15
    list_filter = ('date_of_application', 'faculty', 'course', 'foundation', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status', 'print')
    readonly_fields = ('id_card',)
    search_fields = ('last_name', 'first_name', 'patronymic', 'address',
                     'specialty__name', 'individual_identification_number', 'university')

    def id_card(self, obj):
        return format_html(f"""<img src="{obj.iin_attachment.url}" width="300px">""")


@admin.register(Recovery)
class RecoveryAdmin(CustomAdmin):
    """
    Админ.панель - восстановление в число обучающихся
    """
    entity = 'recovery'
    app = 'Ваше заявление принято.'
    list_per_page = 15
    list_filter = ('date_of_application', 'faculty', 'course', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status', 'print')
    readonly_fields = ('id_card',)
    search_fields = ('last_name', 'first_name', 'patronymic', 'address', 'specialty__name',
                     'individual_identification_number', 'university')

    def id_card(self, obj):
        return format_html(f"""<img src="{obj.iin_attachment.url}" width="300px">""")
