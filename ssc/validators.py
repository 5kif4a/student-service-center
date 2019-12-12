# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
import datetime as dt
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError

# В этом модуле находятся валидаторы

# текущий год
year_ = dt.datetime.now().year
# допустимые разрешения файлов
allowed_extensions = ('pdf', 'jpg', 'jpeg', 'png')
# регулярное выражение для ИИН
iin_regex = '^((0[48]|[2468][048]|[13579][26])0229[1-6]|000229[34]|\d\d((0[13578]|1[02])(0[1-9]|[12]\d|3[01])|(0[469]|11)(0[1-9]|[12]\d|30)|02(0[1-9]|1\d|2[0-8]))[1-6])\d{5}$'
# регулярное выражение для номера телефона (Казахстан)
phone_number_regex = '^\+?77([0124567][0-8]\d{7})$'
# регулярное выражение для символов
alphabet_regex = '^[А-Яа-яA-Za-z]+$'

# валидаторы
alphabet_validator = (RegexValidator(regex=alphabet_regex, message='В этом поле только символы'),)
iin_validator = (RegexValidator(regex=iin_regex, message='Введен неправильный ИИН'),)
phone_number_validator = (RegexValidator(regex=phone_number_regex, message='Введенный номер не соответствует формату'),)
course_validator = (MinValueValidator(1), MaxValueValidator(5))
education_years_validator = (MinValueValidator(1953), MaxValueValidator(year_))

file_ext_validator = FileExtensionValidator(
    allowed_extensions=('jpg', 'jpeg', 'png', 'pdf'),
    message='Допускаются файлы толькок с расширением .jpg, .jpeg, .png, .pdf')


def file_size_validator(value):
    filesize = value.size

    if filesize > 2621440:
        raise ValidationError("Максимальный размер файла, который можно загрузить, составляет 2 МБ.")
    else:
        return value
