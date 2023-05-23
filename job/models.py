from django.db import models

# Create your models here.
class KeywordList(models.Model):
    keywords = models.TextField()