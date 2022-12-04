from django.views import generic
from rest_framework import generics, views


class TestListView(generic.ListView):
	"""Отображение списка доступных тестов"""
	pass


class TestDetailView(generic.DetailView):
	"""Описание теста"""
	pass


class TestProcessAPIView(generics.ListAPIView):
	"""Загрузка процесса прохождения теста"""
	pass


class TestResultView(generic.DetailView):
	"""Отображение результатов прохождения теста"""
	pass


class AnswerProcessingAPIView(views.APIView):
	"""Обработка попытки ответа на вопрос"""
	pass


class TestCompletionView(generic.FormView):
	"""Сохранение результатов прохождения тестов"""
	pass
