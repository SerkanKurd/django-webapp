from django.db import models


class Posts(models.Model):
    id = models.AutoField(primary_key=True)
    post_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    content = models.TextField()
    contentsnippet = models.TextField()
    translated = models.TextField(null=True, blank=True)
    time = models.DateTimeField(null=True, blank=True)
    wordpress_id = models.IntegerField(null=True, blank=True)
    wordpress_url = models.CharField(max_length=255, null=True, blank=True)
    isupdate = models.BooleanField()
    cat = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
