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
        self.fields['specialty'].label = 'Специальность'

