from .models import Comment, Post
from cloudinary.forms import CloudinaryFileField
from django import forms


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'region', 'category')


# class PhotoForm(forms.ModelForm):
    
#     class Meta:
#         model = Photo
#         fields = ('image',)
    
#     image = CloudinaryFileField( 
#         options = { 
#             'tags': "directly_uploaded",
#             'crop': 'thumb', 'width': 250, 'height': 250,
#             'eager': [{ 'crop': 'fill', 'width': 150, 'height': 150 }]
#         })
