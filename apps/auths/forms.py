from unfold.forms import UserChangeForm as BaseUserChangeForm
from unfold.forms import UserCreationForm as BaseUserCreationForm

from apps.auths.models import User


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
