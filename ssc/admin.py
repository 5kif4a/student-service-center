from django.utils.html import format_html
from django.contrib import admin
from django.shortcuts import HttpResponseRedirect
from ssc.models import *
from ssc.utilities import *
# Register your models here.

# Заголовки админ.сайта
admin.site.index_title = 'Центр обслуживания студентов'
admin.site.site_header = 'Центр обслуживания студентов'
admin.site.site_title = 'Административная панель'


# Метод получения всех полей модели(столбцов таблицы)
def get_model_fields(model):
    return [field.name for field in model._meta.get_fields()][2:]


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
    search_fields = get_model_fields(Specialty)


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    """
    Админ.панель для списка университетов
    """
    list_per_page = 30
    list_display = ('name',)
    search_fields = get_model_fields(University)


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
    verify_message = None

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

                send_email(f'{obj.first_name}, ' + self.verify_message, (obj.email,))

                self.message_user(request, f"""Заявление "{obj}" потверждено""")
            # return HttpResponseRedirect(".")
        # Если заявление заполнено неправильно, отправляем письмо с уведомлением
        if "_send_for_correction" in request.POST:
            if obj.status is not 'Отозвано на исправление':
                note = request.POST.get('note')
                message = f'{obj.first_name}, Ваше заявление заполнено неправильно. ' \
                          'Пожалуйста, ознакомьтесь со следующим примечанием и отправьте заявку повторно.\n' \
                          f'Примечание: {note}\nПожалуйста, не отвечайте на это письмо. ' \
                          f'Если у Вас возникнут вопросы, ' \
                          'просим обращаться по номеру 8(7212)56-59-32 (внутренний 2023) или в КарГТУ, ' \
                          '1 корпус, кабинет № 109.\n' \
                          'Если Вы получили это письмо по ошибке, пожалуйста, сообщите нам об этом.\n__\n' \
                          'С уважением, Центр Обслуживания Студентов КарГТУ.'

                obj.status = 'Отозвано на исправление'
                obj.save()

                send_email(message, (obj.email,))
                self.message_user(request, f"Письмо с уведомлением отправлено {obj}")
            else:
                self.message_user(request, f"Письмо с уведомлением уже отправлено {obj}")
        return super().response_change(request, obj)


@admin.register(Reference)
class ReferenceAdmin(CustomAdmin):
    """

    """
    entity = 'reference'
    verify_message = 'Ваша справка готова. ' \
                     'Вы можете получить её в КарГТУ, 1 корпус, кабинет № 109. ' \
                     'При себе необходимо иметь удостоверение личности.\n' \
                     'Пожалуйста, не отвечайте на это письмо. ' \
                     'Если у Вас возникнут вопросы, просим обращаться по номеру 8(7212)56-59-32 (внутренний 2023) или в КарГТУ, ' \
                     '1 корпус, кабинет № 109. ' \
                     'Если Вы получили это письмо по ошибке, пожалуйста, сообщите нам об этом.\n' \
                     '__\n' \
                     'С уважением, Центр Обслуживания Студентов КарГТУ.'
    list_per_page = 15
    list_filter = ('receipt_year', 'exclude_year', 'date_of_application', 'education_form', 'course', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    readonly_fields = ('id_card',)
    search_fields = get_model_fields(Reference)

    def id_card(self, obj):
        return format_html(f"""<img src="{obj.iin_attachment.url}">""")


@admin.register(AcademicLeave)
class AcademicLeaveAdmin(CustomAdmin):
    """

    """
    entity = 'academic-leave'
    verify_message = 'Ваш приказ готов. ' \
                     'Вы можете получить его в КарГТУ, 1 корпус, кабинет № 109. ' \
                     'При себе необходимо иметь удостоверение личности.\n' \
                     'Пожалуйста, не отвечайте на это письмо. ' \
                     'Если у Вас возникнут вопросы, просим обращаться по номеру 8(7212)56-59-32 (внутренний 2023) или в КарГТУ, ' \
                     '1 корпус, кабинет № 109. ' \
                     'Если Вы получили это письмо по ошибке, пожалуйста, сообщите нам об этом.\n' \
                     '__\n' \
                     'С уважением, Центр Обслуживания Студентов КарГТУ.'
    list_per_page = 15
    list_filter = ('date_of_application', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'specialty', 'date_of_application', 'status',
                    'print')
    readonly_fields = ('attachment',)
    search_fields = get_model_fields(Reference)


@admin.register(Duplicate)
class DuplicateAdmin(CustomAdmin):
    """

    """
    entity = 'duplicate'
    verify_message = 'Ваш дубликат готов. ' \
                     'Вы можете получить его в КарГТУ, 1 корпус, кабинет № 109. ' \
                     'При себе необходимо иметь удостоверение личности.\n' \
                     'Пожалуйста, не отвечайте на это письмо. ' \
                     'Если у Вас возникнут вопросы, просим обращаться по номеру 8(7212)56-59-32 (внутренний 2023) или в КарГТУ, ' \
                     '1 корпус, кабинет № 109. ' \
                     'Если Вы получили это письмо по ошибке, пожалуйста, сообщите нам об этом.\n' \
                     '__\n' \
                     'С уважением, Центр Обслуживания Студентов КарГТУ.'
    list_per_page = 15
    list_filter = ('graduation_year', 'date_of_application', 'status')
    list_display = ('last_name', 'first_name', 'patronymic', 'date_of_application', 'status', 'print')
    readonly_fields = ('id_card',)
    search_fields = get_model_fields(Duplicate)

    def id_card(self, obj):
        return format_html(f"""<img src="{obj.iin_attachment.url}">""")