from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from .models import AnswerModel, TestModel, TestGroupModel, QuestionModel, TestingModel


class AnswerInlineFormValidator(BaseInlineFormSet):
	def clean(self):
		super().clean()

		is_correct = False
		is_incorrect = False

		for form in self.forms:
			if form.cleaned_data.get('is_right') is True:
				is_correct = True
			else:
				is_incorrect = True

			if is_correct and is_incorrect:
				return

		raise ValidationError('you must specify the correct and incorrect answer')


class AnswerInline(admin.TabularInline):
	model = AnswerModel
	formset = AnswerInlineFormValidator


class QuestionInline(admin.TabularInline):
	model = QuestionModel


@admin.register(TestGroupModel)
class TestGroupAdmin(admin.ModelAdmin):
	fields = ('title', 'description', )
	list_display = ('title', 'description', )


@admin.register(TestModel)
class TestAdmin(admin.ModelAdmin):
	fields = ('title', 'description', 'groups', )
	list_display = ('title', 'description', )
	inlines = (QuestionInline, )


@admin.register(QuestionModel)
class QuestionAdmin(admin.ModelAdmin):
	fields = ('title', 'position', 'visibility', 'test', )
	list_display = ('title', 'position', 'visibility', 'test')
	list_filter = ('test', 'visibility')
	inlines = (AnswerInline, )
