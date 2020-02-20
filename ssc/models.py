from django.db import models
from django.utils.translation import gettext_lazy as _
from hashid_field import HashidAutoField
from ssc.utilities import *
from ssc.validators import *


# Create your models here.
# Parent models
class Person(models.Model):
    """
    Абстрактный класс-модель - Личность
    """
    last_name = models.CharField(max_length=50, verbose_name=_('Фамилия'), validators=alphabet_validator)

    first_name = models.CharField(max_length=50, verbose_name=_('Имя'), validators=alphabet_validator)

    patronymic = models.CharField(max_length=50, blank=True, verbose_name=_('Отчество'), validators=alphabet_validator)

    individual_identification_number = models.CharField(max_length=12, verbose_name=_('ИИН'), validators=iin_validator)

    email = models.EmailField(verbose_name=_('Электронная почта'))

    address = models.CharField(max_length=500, verbose_name=_('Адрес проживания'))

    phone_number = models.CharField(max_length=16, verbose_name=_('Номер телефона'), validators=phone_number_validator)

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
    course = models.IntegerField(verbose_name=_('Курс'), validators=course_validator)

    group = models.CharField(max_length=50, verbose_name=_('Группа'))

    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name=_('Шифр и название специальности'))

    date_of_application = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подачи заявления'))

    status = models.CharField(max_length=50, choices=application_statuses, default='Не проверено',
                              verbose_name=_('Статус'))

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

    patronymic = models.CharField(max_length=50, blank=True, verbose_name=_('Отчество'))

    individual_identification_number = models.CharField(max_length=12, blank=True, verbose_name=_('ИИН'),
                                                        validators=iin_validator)

    education_form = models.CharField(max_length=50, verbose_name=_('Форма обучения'))

    language_department = models.CharField(max_length=50, verbose_name=_('Языковое отделение'))

    degree = models.CharField(max_length=50, verbose_name=_('Степень обучения'))

    course = models.IntegerField(verbose_name=_('Курс'), validators=course_validator)

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

    receipt_year = models.IntegerField(verbose_name=_('Год поступления'), validators=education_years_validator)

    exclude_year = models.IntegerField(verbose_name=_('Год отчисления'), validators=education_years_validator)

    iin_attachment_front = models.ImageField(upload_to='reference_attachments/',
                                             verbose_name=_('Прикрепление копии документа, удостоверяющего личность - передняя сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='reference_attachments/',
                                            verbose_name=_('Прикрепление копии документа, удостоверяющего личность - обратная сторона'),
                                            validators=[file_size_validator])

    reason = models.CharField(max_length=100, choices=reference_reasons, default='в связи с отчислением',
                              verbose_name=_('Причина'))

    class Meta:
        verbose_name = _('заявление на выдачу справки, не завершившим высшее и послевуз. обр-е')
        verbose_name_plural = _('заявления на выдачу справки, не завершившим высшее и послевуз. обр-е')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class Abroad(Person, Application):
    """
    Прием документов для участия в конкурсе на обучение за рубежом, в том числе академической мобильности
    """

    university = models.ForeignKey(University, on_delete=models.CASCADE, verbose_name=_('Университет'))

    iin_attachment_front = models.ImageField(upload_to='abroad_attachments/',
                                             verbose_name=_('Прикрепление копии документа, удостоверяющего личность - передняя сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='abroad_attachments/',
                                            verbose_name=_('Прикрепление копии документа, удостоверяющего личность - обратная сторона'),
                                            validators=[file_size_validator])

    semester = models.CharField(max_length=200, choices=semesters, verbose_name=_('Семестр'))

    transcript = models.FileField(upload_to='abroad/', blank=True, null=True,
                                  verbose_name=_('Прикрепление копии транскрипта'),
                                  validators=[file_size_validator, file_ext_validator])

    specialty = None

    class Meta:
        verbose_name = _('заявление на участие в конкурсе на обучение за рубежом, в том числе академической мобильности')
        verbose_name_plural = _('заявления на участие в конкурсе на обучение за рубежом, в том числе академической мобильности')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class Hostel(Person, Application):
    """
    Предоставление общежития в высших учебных заведениях
    Государственная услуга
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    place_of_arrival = models.CharField(max_length=200, verbose_name=_('Место прибытия'))

    hostel = models.CharField(max_length=200, choices=hostels, verbose_name=_('Общежитие'))

    iin_attachment_front = models.ImageField(upload_to='hostel_attachments/',
                                             verbose_name=_('Прикрепление копии документа, удостоверяющего личность - передняя сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='hostel_attachments/',
                                            verbose_name=_('Прикрепление копии документа, удостоверяющего личность - обратная сторона'),
                                            validators=[file_size_validator])

    attachment = models.FileField(upload_to='hostel/', blank=True, null=True, verbose_name=_('Прикрепление'),
                                  validators=[file_size_validator, file_ext_validator])

    class Meta:
        verbose_name = _('заявление на предоставление общежития в ВУЗах')
        verbose_name_plural = _('заявления на предоставление общежития в ВУЗах')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


# class Duplicate(Person, Application):
#     """
#     Модель(таблица) для заявления по услуге - "Выдача дубликатов документов о высшем и послевузовском образовании"
#     Государственная услуга
#     """
#     id = HashidAutoField(primary_key=True, min_length=16)
#
#     graduation_year = models.IntegerField(verbose_name=_('Год окончания ВУЗа'), validators=education_years_validator)
#
#     iin_attachment = models.ImageField(upload_to='duplicate/iin',
#                                        verbose_name=_('Прикрепление копии документа, удостоверяющего личность'),
#                                        validators=[file_size_validator])
#
#     duplicate_type = models.CharField(max_length=100, choices=duplicate_types, default='Дубликат диплома',
#                                       verbose_name=_('Тип дубликата'))
#
#     reason = models.CharField(max_length=100, choices=duplicate_reasons, default='утерей',
#                               verbose_name=_('Причина'))
#
#     course = None
#     group = None
#
#     class Meta:
#         verbose_name = _('заявление на выдачу дубликатов документов о высшем и послевузовском образовании')
#         verbose_name_plural = _('заявления на выдачу дубликатов документов о высшем и послевузовском образовании')
#
#     def __str__(self):
#         return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class AcademicLeave(Person, Application):
    """
    Предоставление академических отпусков обучающимся в организациях образования
    Государственная услуга
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    iin_attachment_front = models.ImageField(upload_to='academic_leave_attachments/',
                                             verbose_name=_('Прикрепление копии документа, удостоверяющего личность - передняя сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='academic_leave_attachments/',
                                            verbose_name=_('Прикрепление копии документа, удостоверяющего личность - обратная сторона'),
                                            validators=[file_size_validator])

    attachment = models.FileField(upload_to='hostel/', verbose_name=_('Прикрепление'),
                                  validators=[file_size_validator, file_ext_validator])

    reason = models.CharField(max_length=100, choices=academic_leave_reasons, default='состоянием здоровья',
                              verbose_name=_('Причина'))

    course = None
    group = None

    class Meta:
        verbose_name = _('заявление на предоставление академ.отпусков обучающимся в организациях образования')
        verbose_name_plural = _('заявления на предоставление академ.отпусков обучающимся в организациях образования')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class TransferKSTU(Person, Application):
    """
    Перевод в КарГТУ
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    university = models.CharField(max_length=500, verbose_name=_('Наименование предыдущего ВУЗа)'))

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    foundation = models.CharField(max_length=200, choices=foundation_types, default='на платной основе',
                                  verbose_name=_('Основа обучения'))

    iin_attachment_front = models.ImageField(upload_to='transfer_kstu_attachments/',
                                             verbose_name=_('Прикрепление копии документа, удостоверяющего личность - передняя сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='transfer_kstu_attachments/',
                                            verbose_name=_('Прикрепление копии документа, удостоверяющего личность - обратная сторона'),
                                            validators=[file_size_validator])

    reference = models.FileField(verbose_name=_('Академическая справка'), blank=True,
                                 validators=[file_size_validator, file_ext_validator])

    transcript = models.FileField(verbose_name=_('Копия транскрипта'),
                                  validators=[file_size_validator, file_ext_validator])

    grant = models.FileField(blank=True, null=True, verbose_name=_('Свидительство о образовательном гранте'))

    group = None
    reason = None

    class Meta:
        verbose_name = _('заявление на перевод в КарГТУ')
        verbose_name_plural = _('заявления на перевод в КарГТУ')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class Transfer(Person, Application):
    """
    Перевод в другой ВУЗ
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name=_('Специальность перевода'))

    current_specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name=_('Текущая специальность'),
                                          related_name='current_specialty')

    university = models.CharField(max_length=500, verbose_name=_('Наименование ВУЗа перевода'))

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    foundation = models.CharField(max_length=200, choices=foundation_types, default='на платной основе',
                                  verbose_name=_('Основа обучения'))

    iin_attachment_front = models.ImageField(upload_to='transfer_attachments/',
                                             verbose_name=_('Прикрепление копии документа, удостоверяющего личность - передняя сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='transfer_attachments/',
                                            verbose_name=_('Прикрепление копии документа, удостоверяющего личность - обратная сторона'),
                                            validators=[file_size_validator])

    course = None
    reason = None

    class Meta:
        verbose_name = _('заявление на перевод в другой ВУЗ')
        verbose_name_plural = _('заявления на перевод в другой ВУЗ')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class Recovery(Person, Application):
    """
    Восстановление в число обучающихся
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    university = models.CharField(max_length=500, verbose_name=_('Наименование предыдущего ВУЗа)'))

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    iin_attachment_front = models.ImageField(upload_to='recovery_attachments/',
                                             verbose_name=_('Прикрепление копии документа, удостоверяющего личность - передняя сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='recovery_attachments/',
                                            verbose_name=_('Прикрепление копии документа, удостоверяющего личность - обратная сторона'),
                                            validators=[file_size_validator])

    reference = models.FileField(verbose_name=_('Академическая справка'), blank=True,
                                 validators=[file_size_validator, file_ext_validator])

    transcript = models.FileField(verbose_name=_('Копия транскрипта'),
                                  validators=[file_size_validator, file_ext_validator])

    group = None
    reason = None

    class Meta:
        verbose_name = _('заявление на восстановление в число обучающихся')
        verbose_name_plural = _('заявления на восстановление в число обучающихся')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


# class PlaceOfStudy(Person):
#     """
#     Выдача справки с места учебы
#     """
#     pass


class Notification(models.Model):
    """
    Уведомление о заявлениях
    """
    id = HashidAutoField(primary_key=True, min_length=16)
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата отправки уведомления'))
    application_type = models.CharField(max_length=500, verbose_name=_('Тип заявления'))
    url_for_application = models.URLField(verbose_name=_('Ссылка на заявление'))
    is_showed = models.BooleanField(verbose_name=_('Показано'))

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f'Уведомление: {self.application_type}'
