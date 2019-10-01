from django.shortcuts import render, redirect, HttpResponse
from scc.forms import ReferenceForm
from scc.utility import statuses
# Create your views here.


# главная страница
def index(request):
    return render(request, 'scc/index.html')


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
        return render(request, 'scc/bachelor.html', context)


def postgraduate(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('postgraduate')
        }
        return render(request, 'scc/postgraduate.html', context)


def abroad(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('abroad')
        }
        return render(request, 'scc/abroad.html', context)


def certificate(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('certificate')
        }
        return render(request, 'scc/certificate.html', context)


def hostel(request):
        if request.method == 'POST':
            return redirect('')
        else:
            # form = ReferenceForm()
            context = {
                # 'form': form
                'status': statuses.get('hostel')
            }
            return render(request, 'scc/hostel.html', context)


def duplicate(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('duplicate')
        }
        return render(request, 'scc/duplicate.html', context)


def academic_leave(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('academic-leave')
        }
        return render(request, 'scc/academic-leave.html', context)


# Выдача справки лицам, не завершившим высшее и послевузовское образование
def reference(request):
    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'scc/complete.html')
    else:
        form = ReferenceForm()
        context = {
            'form': form,
            'status': statuses.get('reference')
        }
        return render(request, 'scc/reference.html', context)


def transfer_and_recovery(request):
    if request.method == 'POST':
        return redirect('')
    else:
        # form = ReferenceForm()
        context = {
            # 'form': form
            'status': statuses.get('transfer-and-recovery')
        }
        return render(request, 'scc/transfer-and-recovery.html')


def report(request, obj_id):
    return HttpResponse(f'obj id: {obj_id}')
