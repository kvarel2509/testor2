from .forms import TestResultForm
from .models import AnswerModel, TestModel, QuestionModel, TestingModel

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect
from rest_framework import views, response


class TestListView(LoginRequiredMixin, generic.TemplateView):
	"""Отображение списка доступных тестов"""
	template_name = 'core/test_list.html'

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['object_list'] = [{
			'pk': test.pk,
			'title': test.title,
			'description': test.description,
			'groups': [{
				'pk': group.pk,
				'title': group.title,
				'description': group.description
			} for group in test.groups.all()]
		} for test in TestModel.objects.all().prefetch_related('groups')]

		return ctx


class TestDetailView(LoginRequiredMixin, generic.DetailView):
	"""Описание теста"""
	model = TestModel
	template_name = 'core/test_detail.html'

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		attept = TestingModel.objects.filter(user=self.request.user, test=self.object)
		ctx['attept_last'] = attept.last()
		ctx['attept_count'] = attept.count()
		ctx['groups'] = self.object.groups.all()
		return ctx


class TestStartView(LoginRequiredMixin, generic.RedirectView):
	"""Создание записи о прохождении тестирования и перенаправление на страницу тестирования"""
	def __init__(self, **kwargs):
		self.testing = None
		super().__init__(**kwargs)

	def get(self, request, *args, **kwargs):
		self.testing = TestingModel.objects.create(
			user=self.request.user,
			test_id=self.kwargs.get('pk'),
		)
		return super().get(request, *args, **kwargs)

	def get_redirect_url(self, *args, **kwargs):
		return reverse_lazy('testing-process', kwargs={'pk': self.testing.pk})


class TestingProcessView(LoginRequiredMixin, generic.UpdateView):
	"""Отображение страницы прохождения теста"""
	template_name = 'core/testing_process.html'
	model = TestingModel
	form_class = TestResultForm

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()

		if self.object.is_start:
			return HttpResponseRedirect(redirect_to=reverse_lazy('testing-result', kwargs={'pk': self.object.pk}))

		self.object.is_start = True
		self.object.save()
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['test'] = self.object.test
		return ctx

	def get_success_url(self):
		return reverse_lazy('testing-result', kwargs={'pk': self.kwargs.get('pk')})


class TestDataAPIView(LoginRequiredMixin, views.APIView):
	"""Получение данных теста"""
	def get(self, *args, **kwargs):
		answers = AnswerModel.objects.filter(
			question__test_id=self.kwargs.get('pk'), question__visibility=True
		).order_by('question__position').select_related()

		test_data = dict()

		for answer in answers:
			test_data.setdefault(answer.question_id, dict(
				id=answer.question_id,
				title=answer.question.title,
				answers=list()
			))['answers'].append({'pk': answer.pk, 'title': answer.title, 'is_right': answer.is_right})

		for question in test_data.values():
			question['type_answer'] = 'checkbox' if len([i for i in question['answers'] if i['is_right']]) > 1 else 'radio'

			for answer in question['answers']:
				del answer['is_right']

		return response.Response(list(test_data.values()))


class TestingResultView(LoginRequiredMixin, generic.DetailView):
	"""Отображение результатов прохождения теста"""
	model = TestingModel
	template_name = 'core/testing_result.html'

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		if self.object.correct_answers:
			ctx['percent'] = self.object.correct_answers / (self.object.correct_answers + self.object.wrong_answers) * 100
		else:
			ctx['percent'] = 0

		return ctx


class AnswerProcessingAPIView(LoginRequiredMixin, views.APIView):
	"""Обработка попытки ответа на вопрос"""
	def post(self, *args, **kwargs):
		answers = [int(i) for i in self.request.data.getlist('result')]
		question = QuestionModel.objects.get(pk=self.kwargs.get('pk'))
		result = question.check_answer(answers)
		return response.Response({'result': result})


class RegistrationUserView(generic.CreateView):
	"""Регистрация"""
	form_class = UserCreationForm
	template_name = 'core/registration.html'

	def form_valid(self, form):
		redirect = super().form_valid(form)
		login(self.request, self.object)
		return redirect

	def get_success_url(self):
		return reverse_lazy('test-list')
