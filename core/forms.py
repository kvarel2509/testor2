from core.models import TestingModel

from django import forms


class TestResultForm(forms.ModelForm):
	class Meta:
		model = TestingModel
		fields = ('correct_answers', 'wrong_answers', 'is_completed')
