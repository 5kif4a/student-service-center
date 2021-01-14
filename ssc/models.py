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

    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE,
                                  verbose_name=_('Шифр и название образовательной программы/специальности'))

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
    Услуга переименована в "Заявка на транскрипт обучавшихся в КарТУ"
    """

    id = HashidAutoField(primary_key=True, min_length=16)

    education_form = models.CharField(max_length=10, choices=education_types, default='Очное',
                                      verbose_name=_('Форма обучения'))

    receipt_year = models.IntegerField(verbose_name=_('Год поступления'), validators=education_years_validator)

    exclude_year = models.IntegerField(verbose_name=_('Год отчисления'), validators=education_years_validator)

    # iin_attachment_front = models.ImageField(upload_to='reference_attachments/',
    #                                          verbose_name=_(
    #                                              'Прикрепление копии документа, удостоверяющего личность - передняя '
    #                                              'сторона'),
    #                                          validators=[file_size_validator])
    #
    # iin_attachment_back = models.ImageField(upload_to='reference_attachments/',
    #                                         verbose_name=_(
    #                                             'Прикрепление копии документа, удостоверяющего личность - обратная '
    #                                             'сторона'),
    #                                         validators=[file_size_validator])

    reason = models.CharField(max_length=100, choices=reference_reasons, default='в связи с отчислением',
                              verbose_name=_('Причина'))

    course = models.IntegerField(verbose_name=_('Курс'),
                                 blank=True, null=True,
                                 validators=course_validator)

    # group = models.CharField(max_length=50,
    #                          blank=True, null=True,
    #                          verbose_name=_('Группа'))
    group = None
    address = None

    class Meta:
        verbose_name = _('заявки на транскрипт обучавшихся в КарТУ')
        verbose_name_plural = _('заявки на транскрипт обучавшихся в КарТУ')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class Abroad(Person, Application):
    """
    Прием документов для участия в конкурсе на обучение за рубежом, в том числе академической мобильности
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    address = None

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    # iin_attachment_front = models.ImageField(upload_to='abroad_attachments/',
    #                                          verbose_name=_(
    #                                              'Прикрепление копии документа, удостоверяющего личность - передняя '
    #                                              'сторона'),
    #                                          validators=[file_size_validator])
    #
    # iin_attachment_back = models.ImageField(upload_to='abroad_attachments/',
    #                                         verbose_name=_(
    #                                             'Прикрепление копии документа, удостоверяющего личность - обратная '
    #                                             'сторона'),
    #                                         validators=[file_size_validator])

    # semester = models.CharField(max_length=200, choices=semesters, verbose_name=_('Семестр'))

    passport = models.FileField(upload_to='abroad_attachments/',
                                verbose_name=_('Копия паспорта'),
                                validators=[file_size_validator, file_ext_validator])

    recommendation_letter = models.FileField(upload_to='abroad_attachments/',
                                             verbose_name=_('Рекомендательное письмо'),
                                             validators=[file_size_validator, file_ext_validator])

    transcript = models.FileField(upload_to='abroad_attachments/',
                                  verbose_name=_('Копия транскрипта'),
                                  validators=[file_size_validator, file_ext_validator])

    certificate = models.FileField(upload_to='abroad_attachments/',
                                   verbose_name=_('Сертификат, подтверждающий знание иностранного языка'),
                                   validators=[file_size_validator, file_ext_validator])

    class Meta:
        verbose_name = _(
            'заявление на участие в конкурсе на обучение за рубежом в рамках академической мобильности')
        verbose_name_plural = _(
            'заявления на участие в конкурсе на обучение за рубежом в рамках академической мобильности')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class Hostel(Person, Application):
    """
    Предоставление общежития в высших учебных заведениях
    Государственная услуга
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    individual_identification_number = models.CharField(max_length=12, verbose_name=_('ИИН'), validators=iin_validator)

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    group = models.CharField(max_length=50, blank=True, verbose_name=_('Группа'))

    place_of_arrival = models.CharField(max_length=200, verbose_name=_('Место прибытия (адрес прописки/проживания)'))

    # hostel = models.CharField(max_length=200, choices=hostels, verbose_name=_('Общежитие'))

    is_serpin = models.BooleanField(verbose_name="Участник программы \"Серпiн-2050\"")

    iin_attachment_front = models.ImageField(upload_to='hostel_attachments/',
                                             verbose_name=_(
                                                 'Прикрепление копии документа, удостоверяющего личность - передняя '
                                                 'сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='hostel_attachments/',
                                            verbose_name=_(
                                                'Прикрепление копии документа, удостоверяющего личность - обратная '
                                                'сторона'),
                                            validators=[file_size_validator])

    attachmentProperty = models.FileField(upload_to='hostel_attachments/',
                                          verbose_name=_('Справка об отсутствии (наличии) недвижимого имущества'),
                                          validators=[file_size_validator, file_ext_validator])

    attachmentDeath = models.FileField(upload_to='hostel_attachments/', blank=True, null=True, verbose_name=_(
        'Свидетельство о смерти обоих или единственного родителя либо справка из детского дома'),
                                       validators=[file_size_validator, file_ext_validator])

    attachmentLarge = models.FileField(upload_to='hostel_attachments/', blank=True, null=True,
                                       verbose_name=_('Справка о наличии в семье 4-х и более детей'),
                                       validators=[file_size_validator, file_ext_validator])

    attachmentDisabled = models.FileField(upload_to='hostel_attachments/', blank=True, null=True,
                                          verbose_name=_('Справка о подтверждении инвалидности'),
                                          validators=[file_size_validator, file_ext_validator])

    attachmentKandas = models.FileField(upload_to='hostel_attachments/', blank=True, null=True,
                                        verbose_name=_('Документ о статусе "кандас"'),
                                        validators=[file_size_validator, file_ext_validator])

    message = models.CharField(max_length=200, blank=True, verbose_name=_('Отправленный ответ'))

    address = None

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
    Предоставление и продление академических отпусков обучающимся в организациях образования
    Государственная услуга
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    foundation_type = models.CharField(max_length=200, choices=foundation_types,
                                       default='на платной основе',
                                       verbose_name=_('Основа обучения'))

    reason = models.CharField(max_length=100, choices=academic_leave_reasons, default='состоянием здоровья',
                              verbose_name=_('Причина'))

    is_prolongation = models.BooleanField(verbose_name="Продление академ. отпуска", default=False)

    iin_attachment_front = models.ImageField(upload_to='academic_leave_attachments/',
                                             verbose_name=_(
                                                 'Прикрепление копии документа, удостоверяющего личность - передняя '
                                                 'сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='academic_leave_attachments/',
                                            verbose_name=_(
                                                'Прикрепление копии документа, удостоверяющего личность - обратная '
                                                'сторона'),
                                            validators=[file_size_validator])

    attachment = models.FileField(upload_to='academic_leave_attachments/', verbose_name=_('Прикрепление'),
                                  validators=[file_size_validator, file_ext_validator])

    leave_start = models.DateField(max_length=10, blank=True, verbose_name=_('Начало отпуска'), null=True)

    leave_end = models.DateField(max_length=10, blank=True, verbose_name=_('Конец отпуска'), null=True)

    number = models.IntegerField(max_length=10, blank=True, verbose_name=_('Номер приказа'), null=True)

    course = None
    address = None

    class Meta:
        verbose_name = _('заявление на предоставление и продление академ.отпуска обучающимся в организациях '
                         'образования')
        verbose_name_plural = _('заявления на предоставление и продление академ.отпуска обучающимся в организациях '
                                'образования')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class TransferKSTU(Person, Application):
    """
    Перевод в КарТУ
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    university = models.CharField(max_length=500, verbose_name=_('Наименование предыдущего ВУЗа)'))

    specialty_on_previous_university = models.ForeignKey(Specialty, on_delete=models.CASCADE,
                                                         verbose_name=_('Специальность обучения в предыдущем ВУЗе'),
                                                         related_name='specialty_on_previous_university')

    transfer_specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE,
                                           verbose_name=_('Специальность перевода'),
                                           related_name='transfer_specialty')

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    foundation_on_previous_university = models.CharField(max_length=200, choices=foundation_types,
                                                         default='на платной основе',
                                                         verbose_name=_('Основа обучения в предыдущем ВУЗе'))

    foundation_in_kstu = models.CharField(max_length=200, choices=foundation_types,
                                          default='на платной основе',
                                          verbose_name=_('Основа обучения в КарТУ'))

    iin_attachment_front = models.ImageField(upload_to='transfer_kstu_attachments/',
                                             verbose_name=_(
                                                 'Прикрепление копии документа, удостоверяющего личность - передняя '
                                                 'сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='transfer_kstu_attachments/',
                                            verbose_name=_(
                                                'Прикрепление копии документа, удостоверяющего личность - обратная '
                                                'сторона'),
                                            validators=[file_size_validator])

    permission_to_transfer = models.FileField(upload_to='transfer_kstu_attachments/',
                                              verbose_name=_('Разрешение на перевод с предыдущего ВУЗа'),
                                              validators=[file_size_validator, file_ext_validator])

    certificate = models.FileField(upload_to='transfer_kstu_attachments/',
                                   verbose_name=_('Копия сертификата ЕНТ/КТА'),
                                   validators=[file_size_validator, file_ext_validator])

    transcript = models.FileField(upload_to='transfer_kstu_attachments/',
                                  verbose_name=_('Копия транскрипта'),
                                  validators=[file_size_validator, file_ext_validator])

    grant = models.FileField(upload_to='transfer_kstu_attachments/',
                             blank=True, null=True, verbose_name=_('Свидетельство о образовательном гранте'))

    group = None
    address = None
    specialty = None

    class Meta:
        verbose_name = _('заявление на перевод в КарТУ')
        verbose_name_plural = _('заявления на перевод в КарТУ')

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

    foundation_in_kstu = models.CharField(max_length=200, choices=foundation_types, default='на платной основе',
                                          verbose_name=_('Основа обучения в КарТУ'))

    foundation_in_transfer = models.CharField(max_length=200, choices=foundation_types, default='на платной основе',
                                              verbose_name=_('Основа обучения в ВУЗе перевода'))

    with_grant_preservation = models.BooleanField(default=False, verbose_name=_('с сохранением гранта'))

    # iin_attachment_front = models.ImageField(upload_to='transfer_attachments/', verbose_name=_( 'Прикрепление копии
    # документа, удостоверяющего личность - передняя сторона'), validators=[file_size_validator])
    #
    # iin_attachment_back = models.ImageField(upload_to='transfer_attachments/', verbose_name=_( 'Прикрепление копии
    # документа, удостоверяющего личность - обратная сторона'), validators=[file_size_validator])

    course = None

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

    specialty_on_previous_university = models.ForeignKey(Specialty, on_delete=models.CASCADE,
                                                         verbose_name=_('Специальность обучения в предыдущем ВУЗе'),
                                                         related_name='specialty_on_previous_university_recovery', null=True)

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    iin_attachment_front = models.ImageField(upload_to='recovery_attachments/',
                                             verbose_name=_(
                                                 'Прикрепление копии документа, удостоверяющего личность - передняя '
                                                 'сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='recovery_attachments/',
                                            verbose_name=_(
                                                'Прикрепление копии документа, удостоверяющего личность - обратная '
                                                'сторона'),
                                            validators=[file_size_validator])

    attachment = models.FileField(upload_to='recovery_attachments/',
                                  verbose_name=_('Копия транскрипта/Академическая справка'),
                                  validators=[file_size_validator, file_ext_validator])

    certificate = models.FileField(upload_to='recovery_attachments/',
                                   verbose_name=_('Копия сертификата ЕНТ/КТА'),
                                   validators=[file_size_validator, file_ext_validator])

    group = None
    address = None

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
    APPLICATIONS_TYPES = [('Академическая мобильность', 'Академическая мобильность'),
                          ('Общежитие', 'Общежитие'),
                          ('Дубликаты документов', 'Дубликаты документов'),
                          ('Академическая справка', 'Академическая справка'),
                          ('Академический отпуск', 'Академический отпуск'),
                          ('Перевод в другой ВУЗ', 'Перевод в другой ВУЗ'),
                          ('Перевод в КарТУ', 'Перевод в КарТУ'),
                          ('Восстановление в число обучающихся', 'Восстановление в число обучающихся'),
                          ('Возвращение из акадического отпуска', 'Возвращение из акадического отпуска'),
                          ('Изменение персональных данных', 'Изменение персональных данных'),
                          ('Отчисление', 'Отчисление'),
                          ]

    id = HashidAutoField(primary_key=True, min_length=16)
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата отправки уведомления'))
    application_type = models.CharField(max_length=500, verbose_name=_('Тип заявления'), choices=APPLICATIONS_TYPES)
    url_for_application = models.URLField(verbose_name=_('Ссылка на заявление'))
    is_showed = models.BooleanField(verbose_name=_('Прочитано?'), default=False)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-date']

    def __str__(self):
        return f'Уведомление: {self.application_type}'


class HostelRoom(models.Model):
    """
    Комната в общежитии
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    number = models.IntegerField(max_length=10, verbose_name=_('Номер комнаты'))

    hostel = models.CharField(max_length=200, choices=hostels, verbose_name=_('Общежитие'))

    all_space = models.IntegerField(max_length=10, verbose_name=_('Всего мест'))

    free_space = models.IntegerField(max_length=10, verbose_name=_('Свободных мест'))

    sex = models.CharField(max_length=15, verbose_name=_('Пол комнаты'), choices=room_types, default='Неопределено')

    class Meta:
        verbose_name = _('Комната в общежитии')
        verbose_name_plural = _('Комнаты в общежитии')
        ordering = ["hostel", "number"]

    def __str__(self):
        return "Комната " + str(self.number) + "\n" + self.hostel + "\n" + self.sex


class HostelReferral(Person, Application):
    """
    Направление в общежитие
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    individual_identification_number = models.CharField(max_length=12, verbose_name=_('ИИН'), validators=iin_validator)

    number = models.IntegerField(max_length=10, blank=True, verbose_name=_('Номер направления'), null=True)

    appearance_start = models.DateField(max_length=10, blank=True, verbose_name=_('Время явки (начало)'), null=True)

    appearance_end = models.DateField(max_length=10, blank=True, verbose_name=_('Время явки (конец)'), null=True)

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    is_serpin = models.BooleanField(verbose_name="Участник программы \"Серпiн-2050\"")

    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, blank=True, verbose_name=_('Номер комнаты'),
                             null=True)

    iin_attachment_front = models.ImageField(upload_to='referral_attachments/',
                                             verbose_name=_(
                                                 'Прикрепление копии документа, удостоверяющего личность - передняя '
                                                 'сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='referral_attachments/',
                                            verbose_name=_(
                                                'Прикрепление копии документа, удостоверяющего личность - обратная '
                                                'сторона'),
                                            validators=[file_size_validator])

    attachmentProperty = models.FileField(upload_to='hostel/',
                                          verbose_name=_('Справка об отсутствии (наличии) недвижимого имущества'),
                                          validators=[file_size_validator, file_ext_validator])

    attachmentDeath = models.FileField(upload_to='referral_attachments/', blank=True, null=True, verbose_name=_(
        'Свидетельство о смерти обоих или единственного родителя либо справка из детского дома'),
                                       validators=[file_size_validator, file_ext_validator])

    attachmentLarge = models.FileField(upload_to='referral_attachments/', blank=True, null=True,
                                       verbose_name=_('Справка о наличии в семье 4-х и более детей'),
                                       validators=[file_size_validator, file_ext_validator])

    attachmentDisabled = models.FileField(upload_to='referral_attachments/', blank=True, null=True,
                                          verbose_name=_('Справка о подтверждении инвалидности'),
                                          validators=[file_size_validator, file_ext_validator])

    attachmentKandas = models.FileField(upload_to='referral_attachments/', blank=True, null=True,
                                        verbose_name=_('Документ о статусе "кандас"'),
                                        validators=[file_size_validator, file_ext_validator])

    status = models.CharField(max_length=50, choices=hostel_statuses, default='Не рассмотрено',
                              verbose_name=_('Статус'))

    group = models.CharField(max_length=50, blank=True, verbose_name=_('Группа'))

    message = models.CharField(max_length=500, blank=True, verbose_name=_('Отправленный ответ'))

    date_of_referral = models.DateTimeField(blank=True, null=True, verbose_name=_('Дата выдачи направления'))

    date_of_evict = models.DateTimeField(blank=True, null=True, verbose_name=_('Дата выселения'))

    address = None

    class Meta:
        verbose_name = _('Направление в общежитие')
        verbose_name_plural = _('Направления в общежитие')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


HostelReferral._meta.get_field('date_of_application').verbose_name = 'Дата приема заявления'


class AcademicLeaveReturn(Person, Application):
    """
    Возвращение из академических отпусков обучающихся в организациях образования
    Государственная услуга
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    foundation_type = models.CharField(max_length=200, choices=foundation_types,
                                       default='на платной основе',
                                       verbose_name=_('Основа обучения'))

    reason = models.CharField(max_length=100, choices=academic_leave_reasons, default='состоянием здоровья',
                              verbose_name=_('Причина'))

    iin_attachment_front = models.ImageField(upload_to='academic_leave_return_attachments/',
                                             verbose_name=_(
                                                 'Прикрепление копии документа, удостоверяющего личность - передняя '
                                                 'сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='academic_leave_return_attachments/',
                                            verbose_name=_(
                                                'Прикрепление копии документа, удостоверяющего личность - обратная '
                                                'сторона'),
                                            validators=[file_size_validator])

    attachment = models.FileField(upload_to='academic_leave_return_attachments/', verbose_name=_('Прикрепление'),
                                  validators=[file_size_validator, file_ext_validator])

    leave_end = models.DateField(max_length=10, blank=True, verbose_name=_('Дата выхода из отпуска'), null=True)

    number = models.IntegerField(max_length=10, blank=True, verbose_name=_('Номер приказа'), null=True)

    course = None
    address = None

    class Meta:
        verbose_name = _('заявление на возвращение из академ.отпуска обучающихся в организациях '
                         'образования')
        verbose_name_plural = _('заявления на возвращение из академ.отпуска обучающихся в организациях '
                                'образования')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class PrivateInformationChange(Person, Application):
    """
    Изменение персональных данных об обучающихся в организациях образования
    Государственная услуга
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    foundation_type = models.CharField(max_length=200, choices=foundation_types,
                                       default='на платной основе',
                                       verbose_name=_('Основа обучения'))

    reason = models.CharField(max_length=100, choices=information_change_reasons, default='в связи со сменой '
                                                                                          'удостоверения личности',
                              verbose_name=_('Причина'))

    iin_attachment_front = models.ImageField(upload_to='private_information_change_attachments/',
                                             verbose_name=_(
                                                 'Прикрепление копии документа, удостоверяющего личность - передняя '
                                                 'сторона'),
                                             validators=[file_size_validator])

    iin_attachment_back = models.ImageField(upload_to='private_information_change_attachments/',
                                            verbose_name=_(
                                                'Прикрепление копии документа, удостоверяющего личность - обратная '
                                                'сторона'),
                                            validators=[file_size_validator])

    attachment = models.FileField(upload_to='private_information_change_attachments/',
                                  verbose_name=_('Прикрепление копии свидетельства о браке'),
                                  validators=[file_size_validator, file_ext_validator], blank=True, null=True)

    address = None

    class Meta:
        verbose_name = _('заявление на изменение персональных данных об обучающихся в организациях '
                         'образования')
        verbose_name_plural = _('заявления на изменение персональных данных об обучающихся в организациях '
                                'образования')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class Expulsion(Person, Application):
    """
    Отчисление обучающихся в организациях образования
    Государственная услуга
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    foundation_type = models.CharField(max_length=200, choices=foundation_types,
                                       default='на платной основе',
                                       verbose_name=_('Основа обучения'))

    address = None

    class Meta:
        verbose_name = _('заявление на отчисление обучающихся в организациях '
                         'образования')
        verbose_name_plural = _('заявления на отчисление обучающихся в организациях '
                                'образования')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'


class TransferInside(Person, Application):
    """
    Перевод внутри ВУЗа
    """
    id = HashidAutoField(primary_key=True, min_length=16)

    faculty = models.CharField(max_length=200, choices=faculties, verbose_name=_('Факультет'))

    foundation_type = models.CharField(max_length=200, choices=foundation_types, default='на платной основе',
                                       verbose_name=_('Основа обучения в КарТУ'))

    course = None

    class Meta:
        verbose_name = _('заявление на перевод в другой ВУЗ')
        verbose_name_plural = _('заявления на перевод в другой ВУЗ')

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}. ИИН: {self.individual_identification_number}'
