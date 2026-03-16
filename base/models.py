from django.db import models


# Create your models here.


class Page(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True)

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"Base.Page:{self.title}"


class IndexPage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    # content
    title = models.CharField(max_length=200)
    landing = models.TextField()
    # feature 1
    feature_title = models.CharField(max_length=200)
    feature_content = models.TextField()
    feature_image = models.ImageField(upload_to='images/')
    # features 2
    feature_title_2 = models.CharField(max_length=200)
    feature_content_2 = models.TextField()
    feature_image_2 = models.ImageField(upload_to='images/')
    # features 3
    feature_title_3 = models.CharField(max_length=200)
    feature_content_3 = models.TextField()
    feature_image_3 = models.ImageField(upload_to='images/')
