from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.static import serve

from . import views


# Protected media serving
@login_required(login_url='/')
def protected_serve(request, path, document_root=None, show_indexes=False):
    return serve(request, path, document_root, show_indexes)


bachelor_urls = [path('bachelor', views.bachelor)]

postgraduate_urls = [path('postgraduate', views.postgraduate)]

abroad_urls = [path('abroad', views.AbroadView.as_view()),
               path('abroad/report/<obj_id>', views.AbroadView.render)]

certificate_urls = [path('certificate', views.certificate)]

hostel_urls = [path('hostel', views.HostelView.as_view()),
               path('hostel/report/<obj_id>', views.HostelView.render)]

duplicate_urls = [path('duplicate', views.DuplicateView.as_view()),
                  # path('duplicate/report/<obj_id>/', views.DuplicateView.render)
                  ]

reference_urls = [path('reference', views.ReferenceView.as_view()),
                  path('reference/report/<obj_id>/', views.ReferenceView.render)]

academic_leave_urls = [path('academic-leave', views.AcademicLeaveView.as_view()),
                       path('academic-leave/report/<obj_id>/', views.AcademicLeaveView.render)]

transfer_and_recovery_urls = [path('transfer-and-recovery', views.transfer_and_recovery),
                              path('transfer', views.TransferView.as_view()),
                              path('transfer-kstu', views.TransferKSTUView.as_view()),
                              path('recovery', views.RecoveryView.as_view()),
                              path('transfer-inside', views.TransferInsideView.as_view()),
                              path('transfer/report/<obj_id>/', views.TransferView.render),
                              path('transfer-kstu/report/<obj_id>/', views.TransferKSTUView.render),
                              path('recovery/report/<obj_id>/', views.RecoveryView.render),
                              path('transfer-inside/report/<obj_id>/', views.TransferInsideView.render)]

notifications_urls = [path('notifications', views.get_notifications),
                      path('mark_as_read/<obj_id>', views.mark_as_read)]

check_order_urls = [path('check_order', views.check_order)]

hostel_referral_urls = [path('hostel_referral/report/<obj_id>', views.HostelReferralView.render)]

check_hostel_urls = [path('check_hostel', views.check_hostel),
                     path('hostel_space', views.hostel_space),
                     path('hostel_referral_list', views.hostel_referral_list)]

academic_leave_return_urls = [path('academic-leave-return', views.AcademicLeaveReturnView.as_view()),
                       path('academic-leave-return/report/<obj_id>/', views.AcademicLeaveReturnView.render)]

private_information_change_urls = [path('private-information-change', views.PrivateInformationChangeView.as_view()),
                              path('private-information-change/report/<obj_id>/', views.PrivateInformationChangeView.render)]

expulsion_urls = [path('expulsion', views.ExpulsionView.as_view()),
                                   path('expulsion/report/<obj_id>/', views.ExpulsionView.render)]

key_card_urls = [path('key-card', views.KeyCardView.as_view()),
                  path('key-card/report/<obj_id>/', views.KeyCardView.render)]

reference_student_urls = [path('reference-student', views.ReferenceStudentView.as_view()),
                 path('reference-student/report/<obj_id>/', views.ReferenceStudentView.render)]


urlpatterns = [
                  path('', views.index),
                  url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], protected_serve,
                      {'document_root': settings.MEDIA_ROOT})
              ] + bachelor_urls + \
              postgraduate_urls + \
              abroad_urls + \
              certificate_urls + \
              hostel_urls + \
              duplicate_urls + \
              reference_urls + \
              academic_leave_urls + \
              transfer_and_recovery_urls + \
              notifications_urls + \
              check_order_urls + \
              hostel_referral_urls + \
              check_hostel_urls + \
              academic_leave_return_urls + \
              private_information_change_urls + \
              expulsion_urls + \
              key_card_urls + \
              reference_student_urls
