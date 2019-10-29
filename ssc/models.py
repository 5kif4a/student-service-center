from django.db import models
from hashid_field import HashidAutoField

education_types = [('Очное', 'Очное'), ('Заочное', 'Заочное')]
verify_statuses = [('Не проверено', 'Не проверено'), ('Отозвано на исправление', 'Отозвано на исправление'),
                   ('Одобрено', 'Одобрено')]
reasons = [('Отчисление', 'Отчисление'), ('Перевод в другой университет', 'Перевод в другой университет')]


# Create your models here.
# Parent models
class Person(models.Model):
    """
    Абстрактный класс-модель - Личность
    """
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=10)

    class Meta:
        abstract = True


class Specialty(models.Model):
    """
    Специальность
    """
    id = HashidAutoField(primary_key=True, min_length=16)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class University(models.Model):
    """
    Университет
    """
    id = HashidAutoField(primary_key=True, min_length=16)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Application(models.Model):
    """
    Абстрактный класс-модель - Заявление(форма)
    """
    course = models.IntegerField()
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    date_of_application = models.DateField(auto_now_add=True)
    group = models.CharField(max_length=50)

    class Meta:
        abstract = True


# Main tables
class Rector(models.Model):
    """
    Ректор
    """
    name = models.CharField(max_length=100)
    status = models.BooleanField(unique=True)


class Student(Person):
    """
    Студент
    """
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


# Application models
class Reference(Person, Application):
    """
    Выдача справки лицам, не завершившим высшее и послевузовское образование
    """
    id = HashidAutoField(primary_key=True, min_length=16)
    individual_identification_number = models.CharField(max_length=200)
    education_form = models.CharField(max_length=10, choices=education_types, default='Очное')
    receipt_year = models.DateField()
    exclude_year = models.DateField()
    iin_attachment = models.ImageField(upload_to='references/')
    reason = models.CharField(max_length=30, choices=reasons, default='Отчисление')
    status = models.BooleanField()

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. Группа: {self.group}'


# class Bachelor(Person, Application):
#     """
#     Прием документов и зачисление в высшие учебные заведения
#     для обучения по образовательным программам высшего образования
#     """
#     pass
#
#
# class PostGraduate(Person, Application):
#     """
#     Прием документов и зачисление в высшие учебные заведения
#     для обучения по образовательным программам послевузовского образования
#     """
#     pass
#
#
# class Abroad(Person, Application):
#     """
#     Прием документов для участия в конкурсе на обучение за рубежом, в том числе академической мобильности
#     """
#     pass
#
#
# class Certificate(Person, Application):
#     """
#     Выдача сертификата о сдаче комплексного тестирования
#     """
#     pass
#
#
# class Hostel(Person, Application):
#     """
#     Предоставление общежития в высших учебных заведениях
#     """
#     pass
#
#
# class Duplicate(Person, Application):
#     """
#     Выдача дубликатов документов о высшем и послевузовском образовании
#     """
#     pass
#
#
# class AcademicLeave(Person, Application):
#     """
#     Предоставление академических отпусков обучающимся в организациях образования
#     """
#     pass
#
#
# class TransferAndRecovery(Person, Application):
#     """
#     Перевод и восстановление обучающихся в высших учебных заведениях
#     """
#     pass
#
#
# class PlaceOfStudy(Person):
#     """
#     Выдача справки с места учебы
#     """
#     pass
#
#
# class FreeFood(Person, Application):
#     """
#     Предоставление бесплатного питания отдельным категориям граждан,
#     а также лицам, находящимся под опекой (попечительством) и патронатом,
#     обучающимся и воспитанникам организаций технического и профессионального, послесреднего и высшего образования
#     """
#     pass


# class Report(models.Model):
#     pass
