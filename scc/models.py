from django.db import models

education_types = [('Очное', 'Очное'), ('Заочное', 'Заочное')]


# Create your models here.
class Reference(models.Model):
    id = models.BigAutoField(primary_key=True)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    course = models.IntegerField()
    education_form = models.CharField(max_length=10, choices=education_types, default='Очное')
    group = models.CharField(max_length=10)
    specialty = models.CharField(max_length=50)
    receipt_year = models.DateField()
    exclude_year = models.DateField()
    email = models.EmailField()
    phone_number = models.CharField(max_length=10)
    reason = models.TextField()
