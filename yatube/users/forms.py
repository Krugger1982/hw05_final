from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """ Кастомная форма для создания нового пользователя."""
    class Meta(UserCreationForm.Meta):
        model = User
        # Укажем, какие поля должны быть в этой форме, в каком порядке
        fields = ('first_name', 'last_name', 'username', 'email')
