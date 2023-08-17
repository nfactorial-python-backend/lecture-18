from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        if self.pub_date > timezone.now():
            return False

        return self.pub_date >= timezone.now() - timedelta(hours=24)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField()
