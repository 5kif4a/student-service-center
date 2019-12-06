from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from hashid_field import HashidAutoField
from ssc.utilities import *
import datetime as dt

# Текущий год
year_ = dt.datetime.now().year
iin_regex = '^((0[48]|[2468][048]|[13579][26])0229[1-6]|000229[34]|\d\d((0[13578]|1[02])(0[1-9]|[12]\d|3[01])|(0[469]|11)(0[1-9]|[12]\d|30)|02(0[1-9]|1\d|2[0-8]))[1-6])\d{5}$'
phone_number_regex = '^\+?77([0124567][0-8]\d{7})$'
alphabet_regex = '/^[A-Za-z]+$/'


# Create your models here.
# Parent models
class Person(models.Model):
    """
    Абстрактный класс-модель - Личность
    """
    last_name = models.CharField(max_length=50, verbose_name=_('Фамилия'),
                                 validators=[RegexValidator(regex=alphabet_regex,
                                                            message='В этом поле только символы')])
    first_name = models.CharField(max_length=50, verbose_name=_('Имя'),
                                  validators=[RegexValidator(regex=alphabet_regex,
                                                             message='В этом поле только символы')])
    patronymic = models.CharField(max_length=50, verbose_name=_('Отчество'),
                                  validators=[RegexValidator(regex=alphabet_regex,
                                                             message='В этом поле только символы')])
    individual_identification_number = models.CharField(max_length=12, verbose_name=_('ИИН'),
                                                        validators=[RegexValidator(regex=iin_regex,
                                                                                   message='Введен неправильный ИИН')])
    email = models.EmailField(verbose_name=_('Электронная почта'))
    address = models.CharField(max_length=500, verbose_name=_('Адрес'))
    phone_number = models.CharField(max_length=16, verbose_name=_('Номер телефона'),
                                    validators=[RegexValidator(regex=phone_number_regex,
                                                               message='Введенный номер не соответствует формату')])

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
    course = models.IntegerField(verbose_name=_('Курс'), validators=[MinValueValidator(1), MaxValueValidator(5)])
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
    individual_identification_number = models.CharField(max_length=13, verbose_name=_('ИИН'),
                                                        validators=[RegexValidator(regex=iin_regex,
                                                                                   message='Введен неправильный ИИН')])
    education_form = models.CharField(max_length=50, verbose_name=_('Форма обучения'))
    language_department = models.CharField(max_length=50, verbose_name=_('Языковое отделение'))
    degree = models.CharField(max_length=50, verbose_name=_('Степень обучения'))
    course = models.IntegerField(verbose_name=_('Курс'), validators=[MinValueValidator(1), MaxValueValidator(5)])
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
    education_form = models.CharField(max_length=10, choices=education_types, default='Очное',
                                      verbose_name=_('Форма обучения'))
    receipt_year = models.IntegerField(verbose_name=_('Год поступления'),
                                       validators=[MinValueValidator(1953), MaxValueValidator(year_)])
    exclude_year = models.IntegerField(verbose_name=_('Год отчисления'),
                                       validators=[MinValueValidator(1953), MaxValueValidator(year_)])
    iin_attachment = models.ImageField(upload_to='references/',
                                       verbose_name=_('Прикрепление копии документа, удостоверяющего личность'))
    reason = models.CharField(max_length=100, choices=reference_reasons, default='В связи с отчислением',
                              verbose_name=_('Причина'))
    status = models.CharField(max_length=50, choices=application_statuses, default='Не проверено',
                              verbose_name=_('Статус'))

    class Meta:
        verbose_name = _('заявление на выдачу справки, не завершившим высшее и послевуз. обр-е')
        verbose_name_plural = _('заявления на выдачу справки, не завершившим высшее и послевуз. обр-е')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


# class Abroad(Person, Application):
#     """
#     Прием документов для участия в конкурсе на обучение за рубежом, в том числе академической мобильности
#     """
#     pass
#
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

class Duplicate(Person):
    """
    Модель(таблица) для заявления по услуге - "Выдача дубликатов документов о высшем и послевузовском образовании"
    Государственная услуга
    """
    id = HashidAutoField(primary_key=True, min_length=16)
    graduation_year = models.IntegerField(verbose_name=_('Год окончания ВУЗа'),
                                          validators=[MinValueValidator(1953), MaxValueValidator(year_)])
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name=_('Шифр и название специальности'))
    date_of_application = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подачи заявления'))
    iin_attachment = models.ImageField(upload_to='duplicates/',
                                       verbose_name=_('Прикрепление копии документа, удостоверяющего личность'))
    reason = models.CharField(max_length=30, choices=duplicate_reasons, default='Утеря', verbose_name=_('Причина'))
    duplicate_type = models.CharField(max_length=100, choices=duplicate_types, default='Дубликат диплома',
                                      verbose_name=_('Тип дубликата'))
    status = models.CharField(max_length=50, choices=application_statuses, default='Не проверено',
                              verbose_name=_('Статус'))

    class Meta:
        verbose_name = _('заявление на выдачу дубликатов документов о высшем и послевузовском образовании')
        verbose_name_plural = _('заявления на выдачу дубликатов документов о высшем и послевузовском образовании')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class AcademicLeave(Person):
    """
    Предоставление академических отпусков обучающимся в организациях образования
    Государственная услуга
    """
    id = HashidAutoField(primary_key=True, min_length=16)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name=_('Шифр и название специальности'))
    date_of_application = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подачи заявления'))
    reason = models.CharField(max_length=100, choices=academic_leave_reasons, default='', verbose_name=_('Причина'))
    status = models.CharField(max_length=50, choices=application_statuses, default='Не проверено',
                              verbose_name=_('Статус'))
    attachment = models.FileField(blank=True, null=True, verbose_name=_('Прикрепление'))

    class Meta:
        verbose_name = _('заявление на предоставление академ.отпусков обучающимся в организациях образования')
        verbose_name_plural = _('заявления на предоставление академ.отпусков обучающимся в организациях образования')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class TransferKSTU(Person):
    """
    Перевод в КарГТУ
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    university = models.CharField(max_length=500, verbose_name=_('Наименование предыдущего ВУЗа)'))

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name=_('Шифр и название специальности'))

    date_of_application = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подачи заявления'))

    course = models.IntegerField(verbose_name=_('Курс'),
                                 validators=[MinValueValidator(1), MaxValueValidator(5)])

    foundation = models.CharField(max_length=200, choices=foundation_types, default='на платной основе',
                                  verbose_name=_('Основа обучения'))

    iin_attachment = models.ImageField(upload_to='recovery/',
                                       verbose_name=_('Прикрепление копии документа, удостоверяющего личность'))

    reference = models.FileField(verbose_name=_('Академическая справка'))

    transcript = models.FileField(verbose_name=_('Копия транскрипта'))

    grant = models.FileField(blank=True, null=True, verbose_name=_('Свидительство о образовательном гранте'))

    status = models.CharField(max_length=50, choices=application_statuses, default='Не проверено',
                              verbose_name=_('Статус'))

    class Meta:
        verbose_name = _('заявление на перевод в КарГТУ')
        verbose_name_plural = _('заявления на перевод в КарГТУ')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class Transfer(Person):
    """
    Перевод в другой ВУЗ
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    group = models.CharField(max_length=50, verbose_name=_('Группа'))

    current_specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name=_('Текущая специальность'),
                                          related_name='current_specialty')

    university = models.CharField(max_length=500, verbose_name=_('Наименование ВУЗа перевода'))

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name=_('Специальность перевода'),
                                  related_name='transfer_specialty')
    date_of_application = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подачи заявления'))

    foundation = models.CharField(max_length=200, choices=foundation_types, default='на платной основе',
                                  verbose_name=_('Основа обучения'))

    iin_attachment = models.ImageField(upload_to='recovery/',
                                       verbose_name=_('Прикрепление копии документа, удостоверяющего личность'))

    reference = models.FileField(verbose_name=_('Академическая справка'))

    transcript = models.FileField(verbose_name=_('Копия транскрипта'))

    grant = models.FileField(blank=True, null=True, verbose_name=_('Свидительство о образовательном гранте'))

    status = models.CharField(max_length=50, choices=application_statuses, default='Не проверено',
                              verbose_name=_('Статус'))

    class Meta:
        verbose_name = _('заявление на перевод в другой ВУЗ')
        verbose_name_plural = _('заявления на перевод в другой ВУЗ')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class Recovery(Person):
    """
    Восстановление в число обучающихся
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    university = models.CharField(max_length=500, verbose_name=_('Наименование предыдущего ВУЗа)'))

    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE,
                                  verbose_name=_('Шифр и наименование специальности'))

    date_of_application = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подачи заявления'))

    course = models.IntegerField(verbose_name=_('Курс'), validators=[MinValueValidator(1), MaxValueValidator(5)])

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    iin_attachment = models.ImageField(upload_to='recovery/',
                                       verbose_name=_('Прикрепление копии документа, удостоверяющего личность'))

    reference = models.FileField(verbose_name=_('Академическая справка'))

    transcript = models.FileField(verbose_name=_('Копия транскрипта'))

    status = models.CharField(max_length=50, choices=application_statuses, default='Не проверено',
                              verbose_name=_('Статус'))

    class Meta:
        verbose_name = _('заявление на восстановление в число обучающихся')
        verbose_name_plural = _('заявления на восстановление в число обучающихся')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


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
