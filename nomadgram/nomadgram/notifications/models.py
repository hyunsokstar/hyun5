from django.db import models
from django.db.models import CharField, URLField, TextField, DateTimeField
from nomadgram.users import models as user_models
from nomadgram.images import models as image_models

# Create your models here.
class Notification(image_models.TimeStampedModel):
    TYPE_CHOICES = (
        ('like','Like'),
        ('comment','Comment'),
        ('follow','Follow'),
    )
    # 알림을 생성한 사람
    creator = models.ForeignKey(user_models.User, related_name='creator', on_delete=models.CASCADE)
    to = models.ForeignKey(user_models.User, related_name='to', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20,choices=TYPE_CHOICES)
    image = models.ForeignKey(image_models.Image, on_delete=models.CASCADE, null=True, blank=True)
    comment= models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return 'From: {} - To {}'.format(self.creator, self.to)
