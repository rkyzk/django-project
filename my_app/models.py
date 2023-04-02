from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from cloudinary.models import CloudinaryField


STATUS = ((0, "Draft"), (1, "Submitted"), (2, "Published"))
COMMENT_STATUS = ((0, "original"), (1, "edited"), (2, "deleted"))

REGION = (('N/A', 'N/A'),
          ('NAM', 'North America'),
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

CATEGORY = (('saving animals', 'Saving animals'),
            ('saving aquatic system', 'Saving aquatic system'),
            ('saving soil & trees', 'Saving soil & trees'),
            ('saving resources', 'Saving resources'),
            ('eco-conscious diet', 'eco-conscious diet'),
            ('others', 'Others'))


class Post(models.Model):
    title = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    featured_flag = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    published_on = models.DateTimeField(null=True, blank=True)
    content = models.TextField()
    featured_image = CloudinaryField('image', default='placeholder', blank=True)
    status = models.IntegerField(choices=STATUS, default=0)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)
    region = models.CharField(max_length=30, choices=REGION, default='N/A')
    category = models.CharField(max_length=30, choices=CATEGORY,
                                default='Others')
    bookmark = models.ManyToManyField(User, related_name='bookmarked',
                                      blank=True)


    class Meta:
        ordering = ['-created_on']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def number_of_likes(self):
        return self.likes.count()
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})
    
    def excerpt(self):
        excerpt = str(self.content)[0:99] + "..."
        return excerpt

    def pub_date(self):
        pub_date = self.created_on.strftime("%m/%d/%Y")
        return pub_date


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    # commenter
    name = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="comment_writer") # commenter
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False) # get rid of this
    comment_status = models.IntegerField(choices=COMMENT_STATUS, default=0)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"Comment: {self.body} by {self.name.username}"


class Photo(models.Model):
    image = CloudinaryField('image', blank=True)
