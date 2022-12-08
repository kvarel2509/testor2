from typing import List

from django.db import models
from django.conf import settings


class TestGroupModel(models.Model):
	"""Группа тестов"""

	title = models.CharField('Название группы', max_length=50)
	description = models.TextField('Описание группы', blank=True)

	class Meta:
		verbose_name = 'Группа тестов'
		verbose_name_plural = 'Группы тестов'

	def __str__(self):
		return self.title


class TestModel(models.Model):
	"""Тест"""

	title = models.CharField('Название теста', max_length=50)
	description = models.TextField('Описание теста', blank=True)
	groups = models.ManyToManyField(TestGroupModel, verbose_name='Принадлежность к группам')

	class Meta:
		verbose_name = 'Тест'
		verbose_name_plural = 'Тесты'

	def __str__(self):
		return self.title


class QuestionModel(models.Model):
	"""Вопрос теста"""

	title = models.TextField('Текст вопроса')
	test = models.ForeignKey(TestModel, on_delete=models.CASCADE, verbose_name='Принадлежность к тесту')
	position = models.IntegerField('Позиция вопроса в тесте', default=999)
	visibility = models.BooleanField('Видимость вопроса', default=True)

	class Meta:
		verbose_name = 'Вопрос'
		verbose_name_plural = 'Вопросы'

	def __str__(self):
		return self.title

	def check_answer(self, answers: List[int]):
		right_answer = list(self.answermodel_set.filter(is_right=True).values_list('id', flat=True))
		return sorted(right_answer) == sorted(answers)


class AnswerModel(models.Model):
	"""Ответ на вопрос"""

	title = models.TextField('Текст ответа')
	is_right = models.BooleanField('Правильный ответ', default=False)
	question = models.ForeignKey(QuestionModel, on_delete=models.CASCADE, verbose_name='Принадлежность к вопросу')

	class Meta:
		verbose_name = 'Ответ'
		verbose_name_plural = 'Ответы'

	def __str__(self):
		return self.title


class TestingModel(models.Model):
	"""История прохождения тестов"""

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
	test = models.ForeignKey(TestModel, on_delete=models.CASCADE, verbose_name='Тест')
	date = models.DateTimeField('Дата прохождения', auto_now_add=True)
	correct_answers = models.IntegerField('Количество правильных ответов', default=0)
	wrong_answers = models.IntegerField('Количество неправильных ответов', default=0)
	is_start = models.BooleanField('Тестирование начато', default=False)
	is_completed = models.BooleanField('Тестирование завершено', default=False)
