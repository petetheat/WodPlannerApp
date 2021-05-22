from django.urls import path

from . import views

app_name = 'wodplannerapp'
urlpatterns = [
    path('', views.index_view, name='index'),
    path('newwod/', views.CreateWodView.as_view(), name='create'),
    path('newwod/<str:schema_key>/', views.define_wod, name='definewod'),
    path('woddetails/', views.WodOverview.as_view(), name='wodoverview'),
    path('woddetails/<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('success/', views.success, name='success'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar'),
    path('dayview/<int:year>/<int:month>/<int:day>/', views.day_view, name='dayview')
]
