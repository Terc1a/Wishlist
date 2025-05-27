from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Wishlist(models.Model):
    """
    Wishlist model to store wish information.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Wish(models.Model):
    """
    Wish model to store individual wish information.
    """
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=200)
    item_description = models.TextField()
    item_url = models.URLField()
    item_price = models.FloatField()
    item_image = models.ImageField(upload_to="images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name


class WishLike(models.Model):
    """
    Model to store likes for wishes.
    """
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wishlist', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.wishlist.item_name}"