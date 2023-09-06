from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    REQUIRED_FIELDS = ('email', 'first_name', 'last_name')


class Allergen(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='allergens',
        blank=False,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )


class PhotoQuery(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='queries',
        blank=False,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
    image = models.ImageField(
        upload_to='query/',
        blank=False,
    )
    query_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-query_date']


class Ingredient(models.Model):
    query = models.ForeignKey(
        PhotoQuery,
        on_delete=models.CASCADE,
        related_name='ingredients',
        blank='False',
    )
    name = models.CharField(
        max_length=100,
        blank=False,
    )
