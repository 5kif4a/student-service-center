from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
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
    path('reference', views.ReferenceView.as_view()),
    path('transfer-and-recovery', views.transfer_and_recovery),
    path('reference/report/<obj_id>/', views.ReferenceView.render)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
