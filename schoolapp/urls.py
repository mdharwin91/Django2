"""
URL configuration for schoolapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from schoolweb import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('save_bonafide', views.save_bonafide, name='save_bonafide'),
    path('student_details/', views.student_details, name='student_details'),
    path('student_get/', views.student_get, name='student_get'),
    path('student_update/', views.student_update, name='student_update'),
    path('change_password/', views.change_password, name='change_password'),
    path('setup_mfa/', views.setup_mfa, name='setup_mfa'),
    path('get_fee_details/', views.get_fee_details, name='get_fee_details'),
    path('update_fee_details/', views.update_fee_details, name='update_fee_details'),
    path('get_all_fee_details/', views.get_all_fee_details, name='get_all_fee_details'),
    path('send_whatsapp/', views.send_whatsapp, name='send_whatsapp'),
    path('voucher_save/', views.voucher_save, name='voucher_save'),
    path('get_pending_vouchers/', views.get_pending_vouchers, name='get_pending_vouchers'),
    path('approve_voucher/', views.approve_voucher, name='approve_voucher'),
    path('bonafide_request_save/', views.bonafide_request_save, name='bonafide_request_save'),
    path('get_changes/', views.get_changes, name='get_changes'),
    path('save_changes/', views.save_changes, name='save_changes'),
    path('', include('schoolweb.urls')),
]
