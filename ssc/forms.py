from django.forms import ModelForm, NumberInput, FileInput
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
        }

    def __init__(self, *args, **kwargs):
        super(ReferenceForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].label = 'Специальность'
        self.fields['status'].required = False


class AcademicLeaveForm(ModelForm):
    """
    Форма для заявление услуги - "Предоставление академических отпусков обучающимся в организациях образования"
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
        self.fields['specialty'].label = 'Специальность'
        self.fields['attachment'].label = 'Прикрепление файла копии заключения/решения/свидетельства/повестки'
        self.fields['status'].required = False


class DuplicateForm(ModelForm):
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
        model = Duplicate
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(DuplicateForm, self).__init__(*args, **kwargs)
        self.fields['specialty'].label = 'Специальность'
        self.fields['status'].required = False
