from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from ssc.forms import ReferenceForm
from ssc.models import Reference
from ssc.utility import statuses, render_pdf
from django.contrib.auth.decorators import login_required
# Create your views here.


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
        form = self.form_class(request.POST)
        self.context['form'] = form
        if form.is_valid():
            form.save()
            return render(request, 'ssc/complete.html')
        return render(request, self.template_name, self.context)

    @login_required
    def render(self, obj_id):
        ref = Reference.objects.get(id=obj_id)
        context = {
            'ref': ref
        }
        return render_pdf('report/reference.html', context)


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


def report(request, obj_id):
    return HttpResponse(f'obj id: {obj_id}')
