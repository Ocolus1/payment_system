from django.urls import path
from . import views


urlpatterns = [
	#Leave as empty string for base url
	path('', views.index, name="index"),
	path('details/<mat_no>', views.details, name="details"),
	path('process/', views.process, name="process"),
	path('rec/<user>/<amount>/', views.receipt, name="receipt"),
]
