from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from . import views

bachelor_urls = [path('bachelor', views.bachelor)]

postgraduate_urls = [path('postgraduate', views.postgraduate)]

abroad_urls = [path('abroad', views.AbroadView.as_view()),
               path('abroad/report/<obj_id>', views.AbroadView.render)]

certificate_urls = [path('certificate', views.certificate)]

hostel_urls = [path('hostel', views.HostelView.as_view()),
               path('hostel/report/<obj_id>', views.HostelView.render)]

duplicate_urls = [path('duplicate', views.DuplicateView.as_view()),
                  path('duplicate/report/<obj_id>/', views.DuplicateView.render)]

reference_urls = [path('reference', views.ReferenceView.as_view()),
                  path('reference/report/<obj_id>/', views.ReferenceView.render)]

academic_leave_urls = [path('academic-leave', views.AcademicLeaveView.as_view()),
                       path('academic-leave/report/<obj_id>/', views.AcademicLeaveView.render)]

transfer_and_recovery_urls = [path('transfer-and-recovery', views.transfer_and_recovery),
                              path('transfer', views.TransferView.as_view()),
                              path('transfer-kstu', views.TransferKSTUView.as_view()),
                              path('recovery', views.RecoveryView.as_view()),
                              path('transfer/report/<obj_id>/', views.TransferView.render),
                              path('transfer-kstu/report/<obj_id>/', views.TransferKSTUView.render),
                              path('recovery/report/<obj_id>/', views.RecoveryView.render)]


urlpatterns = [
    path('', views.index)
] + bachelor_urls + \
    postgraduate_urls + \
    abroad_urls + \
    certificate_urls + \
    hostel_urls + \
    duplicate_urls + \
    reference_urls + \
    academic_leave_urls + \
    transfer_and_recovery_urls + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
