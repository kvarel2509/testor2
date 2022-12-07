from django import forms

from core.models import TestingModel


class TestResultForm(forms.ModelForm):
	class Meta:
		model = TestingModel
		fields = ('correct_answers', 'wrong_answers', 'is_completed')
