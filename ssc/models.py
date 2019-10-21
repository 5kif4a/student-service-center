from django.db import models
from hashid_field import HashidAutoField

education_types = [('Очное', 'Очное'), ('Заочное', 'Заочное')]
verify_statuses = [('Не проверено', 'Не проверено'), ('Отозвано на исправление', 'Отозвано на исправление'),
                   ('Одобрено', 'Одобрено')]
reasons = [('Отчисление', 'Отчисление'), ('Перевод в другой университет', 'Перевод в другой университет')]


# Create your models here.
class Reference(models.Model):
    id = HashidAutoField(primary_key=True, min_length=16)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    course = models.IntegerField()
    education_form = models.CharField(max_length=10, choices=education_types, default='Очное')
    group = models.CharField(max_length=10)
    specialty = models.CharField(max_length=50)
    receipt_year = models.DateField()
    exclude_year = models.DateField()
    email = models.EmailField()
    phone_number = models.CharField(max_length=10)
    reason = models.CharField(max_length=30, choices=reasons, default='Отчисление')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. Группа: {self.group}'


class Student(models.Model):
    id = HashidAutoField(primary_key=True, min_length=16)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100)
    individual_identification_number = models.CharField(max_length=200)
    education_form = models.CharField(max_length=50)
    language_department = models.CharField(max_length=50)
    degree = models.CharField(max_length=50)
    course = models.IntegerField()
    faculty = models.CharField(max_length=50)
    specialty = models.CharField(max_length=100)
    student_status = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}'
