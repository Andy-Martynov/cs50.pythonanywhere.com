from django.forms import ModelForm, Textarea, NumberInput, TextInput

from .models import Folder

class FolderForm(ModelForm):
    class Meta:
        model = Folder
        fields = ('name', 'tag', )
        widgets = {
            'name' : TextInput(attrs={'placeholder': 'folder name'}),
            'tag' : TextInput(attrs={'placeholder': 'tag'}),
        }

    def __init__(self, *args, **kwargs):
        super(FolderForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'w3-input w3-round-xlarge w3-light-gray p-1 my-1 mx-0'

