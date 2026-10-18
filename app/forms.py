from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User, Paciente, Atencion

class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, validators=[validate_password])

    class Meta:
        model = User
        fields = ['rut', 'nombre', 'apellido', 'direccion']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este nombre de usuario ya existe.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'direccion']

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['rut', 'nombre', 'apellido', 'direccion','habilitado']


class PacienteEditForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'direccion', 'habilitado']

class AtencionForm(forms.ModelForm):
    class Meta:
        model = Atencion
        fields = ['sbp', 'dbp', 'pulso', 'temperatura', 'saturacion', 'procedimiento','practicante','razonIngreso']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = User.objects.filter(perfil_id='I02', is_active=True)
        if user and user.perfil_id == 'I02' and not user.is_superuser:
            queryset = queryset.filter(pk=user.pk)
        self.fields['practicante'].queryset = queryset
