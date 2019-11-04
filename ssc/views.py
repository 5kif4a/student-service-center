from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from ssc.forms import ReferenceForm
from ssc.models import *
from ssc.utility import *
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
# Create your views here.

# Текущий ректор
rector_name = Rector.objects.filter(status=True)[0].name


# главная страница
def index(request):
    return render(request, 'ssc/index.html')


# Прием документов и зачисление в высшие учебные заведения для обучения
# по образовательным программам высшего образования
def bachelor(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('bachelor')
        }
        return render(request, 'ssc/bachelor.html', context)


def postgraduate(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('postgraduate')
        }
        return render(request, 'ssc/postgraduate.html', context)


def abroad(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('abroad')
        }
        return render(request, 'ssc/abroad.html', context)


def certificate(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('certificate')
        }
        return render(request, 'ssc/certificate.html', context)


def hostel(request):
        if request.method == 'POST':
            return redirect('')
        else:
            # form = ReferenceForm()
            context = {
                # 'form': form
                'status': statuses.get('hostel')
            }
            return render(request, 'ssc/hostel.html', context)


def duplicate(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('duplicate')
        }
        return render(request, 'ssc/duplicate.html', context)


def academic_leave(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('academic-leave')
        }
        return render(request, 'ssc/academic-leave.html', context)


# Выдача справки лицам, не завершившим высшее и послевузовское образование
class ReferenceView(View):

    form_class = ReferenceForm
    template_name = 'ssc/reference.html'
    context = {'status': statuses.get('reference')}

    def get(self, request):
        form = self.form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        self.context['form'] = form

        file = request.FILES['iin_attachment']
        fs = FileSystemStorage()

        if form.is_valid():
            fs.save(file.name, file)
            form.save()

            send_email('Ваше заявление принято. Справка будет готова в течение нескольких дней',
                       (request.POST.get('email', ''),))

            return render(request, 'ssc/complete.html')
        return render(request, self.template_name, self.context)

    @login_required
    def render(self, obj_id):
        ref = Reference.objects.get(id=obj_id)
        if ref.status:
            context = {
                'rector_name': rector_name,
                'ref': ref,
                'qr_code': generate_qr_code('http://www.kstu.kz/')
            }
            return render_pdf('applications/reference.html', context)
        else:
            return HttpResponse('<center><h1>Заявление не потверждено</h1></center>')


def transfer_and_recovery(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('transfer-and-recovery')
        }
        return render(request, 'ssc/transfer-and-recovery.html')

