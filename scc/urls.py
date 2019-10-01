from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('bachelor', views.bachelor),
    path('postgraduate', views.postgraduate),
    path('abroad', views.abroad),
    path('certificate', views.certificate),
    path('hostel', views.hostel),
    path('duplicate', views.duplicate),
    path('academic-leave', views.academic_leave),
    path('reference', views.reference),
    path('transfer-and-recovery', views.transfer_and_recovery),
    path('reference/report/<int:obj_id>/', views.report)
]