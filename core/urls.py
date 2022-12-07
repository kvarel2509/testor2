from django.urls import path, include
from .views import TestListView, TestDetailView, TestingResultView, TestStartView,\
	AnswerProcessingAPIView, TestDataAPIView, TestingProcessView, RegistrationUserView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
	path('', TestListView.as_view(), name='test-list'),
	path('test/', include([
		path('<int:pk>/detail/', TestDetailView.as_view(), name='test-detail'),
		path('<int:pk>/start/', TestStartView.as_view(), name='test-start'),
		path('<int:pk>/data/', TestDataAPIView.as_view(), name='test-data'),
	])),
	path('question/<int:pk>/check/', AnswerProcessingAPIView.as_view(), name='question-check'),
	path('testing/', include([
		path('<int:pk>/process/', TestingProcessView.as_view(), name='testing-process'),
		path('<int:pk>/result/', TestingResultView.as_view(), name='testing-result')
	])),
	path('accounts/', include([
		path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),
		path('logout', LogoutView.as_view(template_name='core/logout.html'), name='logout'),
		path('registration/', RegistrationUserView.as_view(), name='registration')
	]))
]
