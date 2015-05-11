from app.models import UserProfile, Config
from django.contrib.auth.models import User
import floppyforms as forms

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('twitter', 'numcel', 'abre', 'recibemsg')

class OpenForm(forms.Form):
	code = forms.CharField(max_length=10, required=True)

class ConfigForm(forms.ModelForm):
	class Meta:
		model = Config
		fields = ('youtube', 'urlcam')

class EditUsersForm(forms.Form):
	def get_users(self):
		users = User.objects.exclude(username='admin')
		OPTIONS = []
		for u in users:
			OPTIONS.append((str(u.username),str(u.username)))
		return OPTIONS
	def __init__(self, *args, **kwargs):
	        super(EditUsersForm, self).__init__(*args, **kwargs)
	        self.fields['choice_field'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=self.get_users())
