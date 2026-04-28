from django import forms
from .model import models
from schoolapp import settings

# Sample testing component
class InputForm(forms.Form):

	first_name = forms.CharField(max_length = 50, widget=forms.TextInput(attrs={'Placeholder':'First Name', 'class': "textBoxClass"}))
	initial = forms.CharField(max_length = 5, widget=forms.TextInput(attrs={'Placeholder':'Initial', 'class': "textBoxClass"}))
	roll_number = forms.IntegerField(min_value=1, max_value=9999, widget=forms.NumberInput(attrs={'Placeholder': '9999', 'class': "textBoxClass"}))
	# student_class = forms.CharField(max_length = 50, widget=forms.TextInput(attrs={'Placeholder':'STD', 'class': "textBoxClass"}))
	standard = forms.CharField(widget=forms.Select(choices=models.SchoolStandard, attrs={'class': "textBoxClass"}))
	password = forms.CharField(widget = forms.PasswordInput(attrs={'Placeholder':'password', 'class': "textBoxClass"}))

# Login component
class LoginForm(forms.Form):

	username = forms.CharField(max_length = 50, widget=forms.TextInput(attrs={'Placeholder':'Username', 'class': "textBoxClass"}))
	password = forms.CharField(widget = forms.PasswordInput(attrs={'Placeholder':'password', 'class': "textBoxClass"}))


class StudentInfo(forms.Form):
	std = forms.CharField(widget=forms.Select(choices=models.SchoolStandard, attrs={'class': "textBoxClass"}))
	dol = forms.CharField(max_length = 10,required=False, widget=forms.TextInput(attrs={'Placeholder':'dd/mm/yyyy', 'class': "textBoxClass"}))
	mobile = forms.CharField(max_length = 10,required=False, widget=forms.TextInput(attrs={'Placeholder':'Mobile Number', 'class': "textBoxClass"}))
	dob = forms.CharField(max_length = 10,required=False, widget=forms.TextInput(attrs={'Placeholder':'dd/mm/yyyy', 'class': "textBoxClass"}))
	free_edu = forms.CharField(widget=forms.Select(attrs={'class': "textBoxClass"},choices=models.free_edu))
	#free_edu = forms.ChoiceField(widget=forms.Select(choices=models.free_edu, attrs={'class':"textBoxClass"}))
	#status = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': "radio-buttonClass"}),choices=models.Status, initial="Active")

	status = forms.CharField(widget=forms.Select(attrs={'class': "textBoxClass"},choices=models.Status))
	#forms.BooleanField(required=True, initial=True)#forms.CharField(max_length = 50, widget=forms.TextInput(attrs={'Placeholder':'Active/InActive', 'class': "textBoxClass"}))
	planner_sk = forms.CharField(max_length = 8, widget=forms.TextInput(attrs={'Placeholder':'SID000xx', 'class': "textBoxClass"}))
	planner_pk = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': "radio-buttonClass"}),choices=models.profile, initial="Student")
	name = forms.CharField(max_length = 50, widget=forms.TextInput(attrs={'Placeholder':'Student Name', 'class': "textBoxClass"}))
	emis = forms.CharField(max_length = 50,required=False, widget=forms.TextInput(attrs={'Placeholder':'Emis Number', 'class': "textBoxClass"}))
	age = forms.CharField(max_length = 50, widget=forms.TextInput(attrs={'Placeholder':'Age', 'class': "textBoxClass"}))
	doj = forms.CharField(max_length = 10,required=False, widget=forms.TextInput(attrs={'Placeholder':'dd/mm/yyyy', 'class': "textBoxClass"}))

class StudentInfoFetch(forms.Form):
	planner_sk = forms.CharField(max_length = 8, widget=forms.TextInput(attrs={'Placeholder':'SID000xx', 'class': "textBoxClass"}))
	planner_pk = forms.CharField(widget=forms.Select(choices=models.profile, attrs={'class': "textBoxClass"}))

class StudentInfoForBilling(forms.Form):
	planner_sk = forms.CharField(max_length = 8, widget=forms.TextInput(attrs={'Placeholder':'SID000xx', 'class': "textBoxClass"}))
	name = forms.CharField(max_length = 50, widget=forms.TextInput(attrs={'Placeholder':'Student Name', 'class': "textBoxClass"}))
	std = forms.CharField(max_length = 10, widget=forms.TextInput(attrs={'Placeholder':'STD', 'class': "textBoxClass"}))
	mobile = forms.CharField(max_length = 10,required=False, widget=forms.TextInput(attrs={'Placeholder':'Mobile Number', 'class': "textBoxClass"}))