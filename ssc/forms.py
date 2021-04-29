from django.forms import ModelForm, NumberInput
from ssc.models import *
from captcha.fields import ReCaptchaField, ReCaptchaV3


class ReferenceForm(ModelForm):
    """
    Форма для заявление услуги - "Выдача справки лицам, не завершившим высшее и послевузовское образование"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = Reference
        fields = "__all__"
        widgets = {
            'course': NumberInput(attrs={'min': 1, 'max': 5}),
            'receipt_year': NumberInput(attrs={'min': 1953, 'max': year_}),
            'exclude_year': NumberInput(attrs={'min': 1953, 'max': year_})
        }

    def __init__(self, *args, **kwargs):
        super(ReferenceForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].label = 'Образовательная программа/специальность'
        self.fields['status'].required = False


class AcademicLeaveForm(ModelForm):
    """
    Форма для заявление услуги - "Предоставление и продление академических отпусков обучающимся в организациях образования"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = AcademicLeave
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AcademicLeaveForm, self).__init__(*args, **kwargs)
        self.fields['reason'].label = 'Причина (в связи)'
        self.fields['specialty'].label = 'Образовательная программа/специальность'
        self.fields['attachment'].label = 'Прикрепление файла копии заключения/решения/свидетельства/повестки/справки'
        self.fields['status'].required = False


class AbroadForm(ModelForm):
    """
    Форма для заявление услуги - "Прием документов для участия в конкурсе на обучение за рубежом, в том числе академической мобильности"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = Abroad
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AbroadForm, self).__init__(*args, **kwargs)
        self.fields['status'].required = False


class HostelForm(ModelForm):
    """
    Форма для заявление услуги - "Предоставление общежития в высших учебных заведениях"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = Hostel
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(HostelForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].label = 'Образовательная программа/специальность'
        self.fields['group'].required = False
        self.fields['status'].required = False
        self.fields['place_of_arrival'].label = 'Место прибытия (адрес прописки/проживания) (Область, район, ' \
                                                'нас. пункт, улица, дом, квартира) '

    def localize(self):
        self.fields['last_name'].label = 'Тегі'
        self.fields['first_name'].label = 'Аты'
        self.fields['patronymic'].label = 'Жөні'
        self.fields['individual_identification_number'].label = 'ЖСН'
        self.fields['email'].label = 'Электронды поштасы'
        self.fields['phone_number'].label = 'Нөмір телефоны'
        self.fields['course'].label = 'Курсы'
        self.fields['faculty'].label = 'Факультеті'
        self.fields['group'].label = 'Тобы'
        self.fields['specialty'].label = 'Мамандығы'
        self.fields['is_serpin'].label = '«Серпін-2050» бағдарламасының қатысушысы'
        self.fields['place_of_arrival'].label = 'Келген жері (мекен-жайы)'
        self.fields['iin_attachment_front'].label = 'Жеке басын куәландыратын құжаттың көшірмесін бекіту-алдыңғы жағы'
        self.fields['iin_attachment_back'].label = 'Жеке басын куәландыратын құжаттың көшірмесін бекіту-артқы жағы'
        self.fields['attachmentProperty'].label = 'Жылжымайтын мүліктің жоқ (бар) екендігі туралы анықтама'
        self.fields[
            'attachmentDeath'].label = 'Екі немесе жалғыз ата-ананың қайтыс болуы туралы куәлік немесе балалар үйінен анықтама'
        self.fields['attachmentLarge'].label = 'Отбасында 4 және одан да көп баланың болуы туралы анықтама'
        self.fields['attachmentDisabled'].label = 'Мүгедектікті растау туралы анықтама'
        self.fields['attachmentKandas'].label = '"Кандас" мәртебесі туралы құжат'


# class DuplicateForm(ModelForm):
#     """
#     Форма для заявление услуги - "Выдача справки лицам, не завершившим высшее и послевузовское образование"
#     """
#     captcha = ReCaptchaField(
#         widget=ReCaptchaV3(
#             attrs={
#                 'required_score': 0.85
#             }
#         )
#     )
#
#     class Meta:
#         model = Duplicate
#         fields = "__all__"
#
#     def __init__(self, *args, **kwargs):
#         super(DuplicateForm, self).__init__(*args, **kwargs)
#         self.fields['reason'].label = 'Причина (в связи)'
#         self.fields['specialty'].label = 'Специальность'
#         self.fields['status'].required = False


class TransferForm(ModelForm):
    """
    Форма для заявление услуги - "Перевод в другой ВУЗ"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    widgets = {
        'course': NumberInput(attrs={'min': 1, 'max': 5})
    }

    class Meta:
        model = Transfer
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)
        self.fields['university'].label = 'ВУЗ перевода'
        self.fields['status'].required = False


class TransferKSTUForm(ModelForm):
    """
    Форма для заявление услуги - "Перевод в КарТУ"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    widgets = {
        'course': NumberInput(attrs={'min': 1, 'max': 5})
    }

    class Meta:
        model = TransferKSTU
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(TransferKSTUForm, self).__init__(*args, **kwargs)
        self.fields['university'].label = 'Предыдущий ВУЗ'
        self.fields['grant'].label = 'Свидетельство о образовательном гранте(если грант)'
        self.fields['status'].required = False


class RecoveryForm(ModelForm):
    """
    Форма для заявление услуги - "Восстановление в число обучающихся"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    widgets = {
        'course': NumberInput(attrs={'min': 1, 'max': 5})
    }

    class Meta:
        model = Recovery
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(RecoveryForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].label = 'Образовательная программа/специальность в КарТУ'
        self.fields[
            'specialty_on_previous_university'].label = 'Образовательная программа/специальность в предыдущем ВУЗе'
        self.fields['faculty'].label = 'Факультет в КарТУ'
        self.fields['university'].label = 'Предыдущий ВУЗ'
        self.fields['status'].required = False


class HostelReferralForm(ModelForm):
    """
    Форма для заявление услуги - "Направление в общежития в высших учебных заведениях"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = HostelReferral
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(HostelReferralForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].label = 'Образовательная программа/специальность'
        self.fields['group'].required = False
        self.fields['status'].required = False


class AcademicLeaveReturnForm(ModelForm):
    """
    Форма для заявление услуги - "Возвращение из академических отпусков обучающихся в организациях образования"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = AcademicLeaveReturn
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AcademicLeaveReturnForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].label = 'Образовательная программа/специальность'
        self.fields['reason'].label = 'Причина (в связи)'
        self.fields['attachment'].label = 'Прикрепление файла копии справки/военного билета/свидетельства о рождении'
        self.fields['status'].required = False


class PrivateInformationChangeForm(ModelForm):
    """
    Форма для заявление услуги - "Изменение персональных данных об обучающихся в организациях образования"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = PrivateInformationChange
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(PrivateInformationChangeForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].label = 'Образовательная программа/специальность'
        self.fields['reason'].label = 'Причина (в связи)'
        self.fields['status'].required = False


class ExpulsionForm(ModelForm):
    """
    Форма для заявление услуги - "Отчисление обучающихся в организациях образования"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = Expulsion
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ExpulsionForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].label = 'Образовательная программа/специальность'
        self.fields['status'].required = False


class TransferInsideForm(ModelForm):
    """
    Форма для заявление услуги - "Перевод внутри ВУЗа"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = TransferInside
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(TransferInsideForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].label = 'Образовательная программа/специальность обучения'
        self.fields['specialty_to'].label = 'Образовательная программа/специальность перевода'
        self.fields['status'].required = False


class KeyCardForm(ModelForm):
    """
    Форма для заявление услуги - "Выдача ключ-карты"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = KeyCard
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(KeyCardForm, self).__init__(*args, **kwargs)
        self.fields['status'].required = False


class ReferenceStudentForm(ModelForm):
    """
    Форма для заявление услуги - "Выдача транскрипта обучающимся"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = ReferenceStudent
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ReferenceStudentForm, self).__init__(*args, **kwargs)
        self.fields['status'].required = False


class KeyCardFirstForm(ModelForm):
    """
    Форма для заявление услуги - "Выдача ключ-карты"
    """
    captcha = ReCaptchaField(
        widget=ReCaptchaV3(
            attrs={
                'required_score': 0.85
            }
        )
    )

    class Meta:
        model = KeyCardFirst
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(KeyCardFirstForm, self).__init__(*args, **kwargs)
        self.fields['status'].required = False