from django.utils.html import format_html
from django.contrib import admin
from .models import *
# Register your models here.

admin.site.site_header = 'Student service center'


def get_model_fields(model):
    return [field.name for field in model._meta.get_fields()][1:]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_per_page = 30
    list_filter = ('education_form', 'language_department', 'degree', 'course', 'faculty', 'specialty',
                   'student_status')
    list_display = get_model_fields(Student)
    search_fields = get_model_fields(Student)


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_per_page = 15
    list_filter = ('receipt_year', 'exclude_year', 'education_form', 'course')
    list_display = ('last_name', 'first_name', 'patronymic', 'course', 'group', 'specialty',
                    'receipt_year', 'exclude_year', 'phone_number', 'print', 'verify')
    search_fields = get_model_fields(Reference)

    def print(self, obj):
        url = f'/reference/report/{obj.id}'
        return format_html(f"""
        <input type="button" class="button" value="Print" onclick="window.open('{url}', '_blank')">
        """)

    def verify(self, obj):
        return format_html(f"""
        <input type="button" class="button" value="Verify">
        """)
