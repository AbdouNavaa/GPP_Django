from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from django.utils.text import slugify
# Create your models here.

bancs = (
    ('BMCI','bmci'),
    ('BNM','BNM'),
    ('Orabanc','orabanc'),
)
class Prof(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image  = models.ImageField(upload_to='profile/',null=True,blank=True)
    compte = models.CharField(max_length=50)
    banc = models.CharField(max_length=15 , choices=bancs)
    role = models.CharField(max_length=50,default='user')
    # email = models.EmailField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
        
    def save(self,*args, **kwargs):
        self.slug = slugify(self.user.username)
        super(Prof,self).save(*args, **kwargs)
    def __str__(self):
        return self.user.username        
        
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Prof.objects.create(user=instance)

