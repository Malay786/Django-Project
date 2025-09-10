from django.forms import ModelForm
from .models import Room

# __all__ will give every field inside the Room model
# there are other ways too

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__' 