from django.forms import ModelForm, DateInput, Textarea, NumberInput
from scc.models import Reference
from captcha.fields import ReCaptchaField


class ReferenceForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Reference
        fields = "__all__"
        widgets = {
            'course': NumberInput(attrs={'min': 1, 'max': 5}),
            'receipt_year': DateInput(attrs={'type': 'date'}),
            'exclude_year': DateInput(attrs={'type': 'date'}),
            'reason': Textarea(attrs={'rows': 5, 'style': 'resize:none;'})
        }

    def __init__(self, *args, **kwargs):
        super(ReferenceForm, self).__init__(*args, **kwargs)
        self.fields['last_name'].label = 'Фамилия'
        self.fields['first_name'].label = 'Имя'
        self.fields['patronymic'].label = 'Отчество'
        self.fields['course'].label = 'Курс'
        self.fields['group'].label = 'Группа'
        self.fields['specialty'].label = 'Специальность'
        self.fields['education_form'].label = 'Форма обучения'
        self.fields['receipt_year'].label = 'Год поступления'
        self.fields['exclude_year'].label = 'Год отчисления'
        self.fields['email'].label = 'Адрес электронной почты'
        self.fields['phone_number'].label = 'Контактный номер телефона'
        self.fields['reason'].label = 'Причина'
