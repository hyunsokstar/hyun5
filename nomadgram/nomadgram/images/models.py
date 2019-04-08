from django.db import models
# Create your models here.
from django.db import models
from django.db import models
from nomadgram.users import models as user_models
from taggit.managers import TaggableManager

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Image(TimeStampedModel):
    file = models.ImageField()
    location = models.CharField(max_length=140)
    caption = models.TextField()
    creator = models.ForeignKey(user_models.User, null=True, on_delete=models.CASCADE, related_name="images")
    tags = TaggableManager()

    def __str__(self):
        return '{}, {}'.format(self.file, self.caption)

    @property
    def like_count(self):
        return self.likes.all().count()

    # 댓글의 개수
    @property
    def comment_count(self):
        return self.comments.all().count()




class Comment(TimeStampedModel):
    message = models.TextField()
    creator = models.ForeignKey(user_models.User, null=True, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, null= True, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return self.message


class Like(TimeStampedModel):
    creator = models.ForeignKey(user_models.User, null=True, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, null=True, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return 'User: {} - Image Caption: {}'.format(self.creator.username, self.image.caption)
