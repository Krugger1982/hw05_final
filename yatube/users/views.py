from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    # после успешной регистрации пользователь переадресуется на главную
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
