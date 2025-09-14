from django.forms import ModelForm
from .models import Room
from django.contrib.auth.models import User

# __all__ will give every field inside the Room model
# there are other ways too

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__' 
        exclude = ['host', 'participants']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']