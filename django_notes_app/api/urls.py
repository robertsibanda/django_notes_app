from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_creat_notes),
    path('update/<int:pk>', views.note_update_view),
    path('delete/<int:pk>', views.note_delete_view),
    path('note/<int:pk>', views.note_detail_view),
    path('login', views.login),
    path('signup', views.signup),
]