from django.forms import ModelForm, DateInput, NumberInput, FileInput
from ssc.models import Reference
from captcha.fields import ReCaptchaField, ReCaptchaV3


class ReferenceForm(ModelForm):
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
            'receipt_year': DateInput(attrs={'type': 'date'}),
            'exclude_year': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ReferenceForm, self).__init__(*args, **kwargs)
        self.fields['last_name'].label = 'Фамилия'
        self.fields['first_name'].label = 'Имя'
        self.fields['patronymic'].label = 'Отчество'
        self.fields['individual_identification_number'].label = 'ИИН'
        self.fields['course'].label = 'Курс'
        self.fields['group'].label = 'Группа'
        self.fields['specialty'].label = 'Специальность'
        self.fields['education_form'].label = 'Форма обучения'
        self.fields['receipt_year'].label = 'Год поступления'
        self.fields['exclude_year'].label = 'Год отчисления'
        self.fields['email'].label = 'Электронная почта'
        self.fields['phone_number'].label = 'Номер телефона'
        self.fields['iin_attachment'].label = 'Копия удостоверения'
        self.fields['reason'].label = 'Причина'
        self.fields['captcha'].required = False
