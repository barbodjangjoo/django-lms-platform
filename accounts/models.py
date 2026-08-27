from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    GENDER_CHOICES = (
        ('male', _('Male')),
        ('female', _('Female')),
    )

    FIND_CHOICES = (
        ('instagram', _('Instagram')),
        ('members', _('Members')),
        ('friends', _('Friends and Family')),
        ('work', _('Manager & Co-worker')),
        ('other', _('Other'))
    )

    EDUCATIONAL_CHOICES = (
        ('1',_('Student')),
        ('2', _('High School')),
        ('3', _('Bachelor')),
        ('4', _('Master')),
        ('5', _('PhD')),
        )


    first_name = models.CharField(_('First name'), max_length=255, blank=True, db_index=True) 
    last_name = models.CharField(_('Last Name'), max_length=255, blank=True, db_index=True) 
    birth_date = models.DateField(_('Birth date'), blank=True, null=True) 
    gender = models.CharField(_('Gender'),max_length=6 , choices=GENDER_CHOICES, blank=True)

    phone_number = models.CharField(_('Phone number'), max_length=11, unique=True, db_index=True)
    email = models.EmailField(_('Email'), blank=True, unique=True, db_index=True)
    city = models.CharField(_('city'),max_length=50, blank=True) 
    address = models.TextField(blank=True, null=True)

    profile_picture = models.ImageField(_('Profile Picture'), upload_to='media/profile_pic/', blank=True,)
    cover_profile = models.ImageField(_('cover_profile'), upload_to='media/cover_profile/', blank=True,)
    username = models.CharField(_('Username') ,max_length=50, blank=True, unique=True)

    find = models.CharField(_('How did you find us?'), max_length=9,choices=FIND_CHOICES, blank=True)
    educational_status = models.CharField(_('Educational status'), max_length=1,choices=EDUCATIONAL_CHOICES, blank=True, null=True)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    
    def __str__(self):
        return f'{self.first_name} - {self.last_name}'


