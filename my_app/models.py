from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

STATUS = ((0, "Draft"), (1, "Submitted"), (2, "Published"))

REGION = (('N/A', 'N/A'),
          ('NAM', 'North Amrica'),
          ('CAM', 'Central America'),
          ('CRB', 'Caribbean'),
          ('SAM', 'South America'),
          ('NEU', 'Northern Europe'),
          ('WEU', 'Western Europe'),
          ('EEU', 'Eastern Europe'),
          ('SEU', 'Southern Europe'),
          ('NAF', 'North Africa'),
          ('WAF', 'Western Africa'),
          ('MAF', 'Middle Africa'),
          ('EAF', 'Eastern Africa'),
          ('SAF', 'Southern Africa'),
          ('SAF', 'Southern Africa'),
          ('WAS', 'Western Asia'),
          ('CAS', 'Central Asia'),
          ('EAS', 'Eastern Asia'),
          ('SAS', 'Southern Asia'),
          ('SAS', 'Southeastern Asia'),
          ('ANZ', 'Australia and New Zealand'),
          ('PIS', 'Pacific Islands'))

CATEGORY = (('others', 'others'),)


class Post(models.Model):
    title = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT,
                               default=1, related_name="posts")
    featured_flag = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    featured_image = CloudinaryField('image', default='placeholder')
    status = models.IntegerField(choices=STATUS, default=0)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)
    region = models.CharField(max_length=30, choices=REGION, default='N/A')
    category = models.CharField(max_length=30, choices=CATEGORY,
                                default='others')
    bookmark = models.ManyToManyField(User, related_name='bookmarked', blank=True)

 
    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def number_of_likes(self):
        return self.likes.count()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    name = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="comment_writer")
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"Comment: {self.body} by {self.name.username}"
