from django.db import models
from django.utils.translation import gettext_lazy as _
from hashid_field import HashidAutoField
from ssc.choices import *


# Create your models here.
# Parent models
class Person(models.Model):
    """
    Абстрактный класс-модель - Личность
    """
    last_name = models.CharField(max_length=50, verbose_name=_('Фамилия'))
    first_name = models.CharField(max_length=50, verbose_name=_('Имя'))
    patronymic = models.CharField(max_length=50, verbose_name=_('Отчество'))
    email = models.EmailField(verbose_name=_('Электронная почта'))
    phone_number = models.CharField(max_length=12, verbose_name=_('Номер телефона'))

    class Meta:
        abstract = True


class Specialty(models.Model):
    """
    Специальность
    """
    id = HashidAutoField(primary_key=True, min_length=16)
    name = models.CharField(max_length=200, verbose_name=_('Шифр и название специальности'))

    class Meta:
        verbose_name = _('специальность')
        verbose_name_plural = _('специальности')

    def __str__(self):
        return self.name


class University(models.Model):
    """
    Университет
    """
    id = HashidAutoField(primary_key=True, min_length=16)
    name = models.CharField(max_length=200, verbose_name=_('Название университета'))

    class Meta:
        verbose_name = _('университет')
        verbose_name_plural = _('университеты')

    def __str__(self):
        return self.name


class Application(models.Model):
    """
    Абстрактный класс-модель - Заявление(форма)
    """
    course = models.IntegerField(verbose_name=_('Курс'))
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name=_('Шифр и название специальности'))
    date_of_application = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подачи заявления'))
    group = models.CharField(max_length=50, verbose_name=_('Группа'))

    class Meta:
        abstract = True


# Main tables
class Rector(models.Model):
    """
    Ректор
    """
    name = models.CharField(max_length=100, verbose_name=_('ФИО ректора'))
    status = models.BooleanField(unique=True, verbose_name=_('Статус ректора'))

    class Meta:
        verbose_name = _('Ректор')
        verbose_name_plural = _('Ректоры')


class Student(models.Model):
    """
    Студент
    """
    last_name = models.CharField(max_length=50, verbose_name=_('Фамилия'))
    first_name = models.CharField(max_length=50, verbose_name=_('Имя'))
    patronymic = models.CharField(max_length=50, verbose_name=_('Отчество'))
    individual_identification_number = models.CharField(max_length=13, verbose_name=_('ИИН'))
    education_form = models.CharField(max_length=50, verbose_name=_('Форма обучения'))
    language_department = models.CharField(max_length=50, verbose_name=_('Языковое отделение'))
    degree = models.CharField(max_length=50, verbose_name=_('Степень обучения'))
    course = models.IntegerField(verbose_name=_('Курс'))
    faculty = models.CharField(max_length=50, verbose_name=_('Факультет'))
    specialty = models.CharField(max_length=100, verbose_name=_('Специальность'))
    student_status = models.CharField(max_length=50, verbose_name=_('Статус студента'))

    class Meta:
        verbose_name = _('студент')
        verbose_name_plural = _('студенты')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}'


# Application models
class Reference(Person, Application):
    """
    Модель(таблица) для заявления по услуге - "Выдача справки лицам, не завершившим высшее и послевузовское образование"
    Государственная услуга
    """
    id = HashidAutoField(primary_key=True, min_length=16)
    individual_identification_number = models.CharField(max_length=12, verbose_name=_('ИИН'))
    education_form = models.CharField(max_length=10, choices=education_types, default='Очное',
                                      verbose_name=_('Форма обучения'))
    receipt_year = models.DateField(verbose_name=_('Год поступления'))
    exclude_year = models.DateField(verbose_name=_('Год отчисления'))
    iin_attachment = models.ImageField(upload_to='references/', verbose_name=_('Прикрепление копии ИИН'))
    reason = models.CharField(max_length=30, choices=reference_reasons, default='В связи с отчислением',
                              verbose_name=_('Причина'))
    status = models.CharField(max_length=50, choices=application_statuses, default='Не проверено',
                              verbose_name=_('Статус'))

    class Meta:
        verbose_name = _('заявление на выдачу справки, не завершившим высшее и послевуз. обр-е')
        verbose_name_plural = _('заявления на выдачу справки, не завершившим высшее и послевуз. обр-е')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


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
#     Государственная услуга
#     """
#     place_of_arrival = models.CharField(max_length=200, verbose_name=_('Место прибытия'))
#
#     class Meta:
#         verbose_name = _('заявление на предоставление общежития в ВУЗах')
#         verbose_name_plural = _('заявления на предоставление общежития в ВУЗах')

#
#
class Duplicate(Person):
    """
    Модель(таблица) для заявления по услуге - "Выдача дубликатов документов о высшем и послевузовском образовании"
    Государственная услуга
    """
    id = HashidAutoField(primary_key=True, min_length=16)
    individual_identification_number = models.CharField(max_length=12, verbose_name=_('ИИН'))
    graduation_year = models.DateField(verbose_name=_('Год окончания ВУЗа'))
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name=_('Шифр и название специальности'))
    date_of_application = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подачи заявления'))
    iin_attachment = models.ImageField(upload_to='references/', verbose_name=_('Прикрепление копии ИИН'))
    reason = models.CharField(max_length=30, choices=duplicate_reasons, default='Утеря', verbose_name=_('Причина'))
    status = models.CharField(max_length=50, choices=application_statuses, default='Не проверено',
                              verbose_name=_('Статус'))

    class Meta:
        verbose_name = _('заявление на выдачу дубликатов документов о высшем и послевузовском образовании')
        verbose_name_plural = _('заявления на выдачу дубликатов документов о высшем и послевузовском образовании')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'
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
