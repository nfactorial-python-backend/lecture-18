from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


# Create your tests here.
class QuestionModelTests(TestCase):
    def test_simple_question(self):
        q = Question(question_text="How are you?", pub_date=timezone.now())
        self.assertIs("How are you?", q.question_text)

    def test_was_published_recently_true(self):
        q = Question(question_text="How are you?", pub_date=timezone.now())
        self.assertIs(True, q.was_published_recently())

    def test_was_published_recently_past_10_hours(self):
        past_date = timezone.now() - timedelta(hours=10)
        q = Question(question_text="How are you?", pub_date=past_date)
        self.assertIs(True, q.was_published_recently())

    def test_was_published_recently_false(self):
        past_date = timezone.now() - timedelta(hours=25)
        q = Question(question_text="How are you?", pub_date=past_date)
        self.assertIs(False, q.was_published_recently())

    def test_was_published_recently_future_false(self):
        future_date = timezone.now() + timedelta(days=1)
        q = Question(question_text="How are you?", pub_date=future_date)
        self.assertIs(False, q.was_published_recently())


class QuestionViewTests(TestCase):
    def test_index(self):
        q1 = Question(question_text="Как дела?", pub_date=timezone.now())
        q2 = Question(question_text="Как сегодня погода?", pub_date=timezone.now())
        q3 = Question(question_text="Как вас зовут?", pub_date=timezone.now())

        q1.save()
        q2.save()
        q3.save()

        response = self.client.get(reverse("polls:index"))

        self.assertIs(200, response.status_code)
        self.assertQuerysetEqual([q3, q2, q1], response.context["questions"])

    def test_index_empty(self):
        response = self.client.get(reverse("polls:index"))

        self.assertIs(200, response.status_code)
        self.assertContains(response, "Нет голосований")
        self.assertQuerysetEqual([], response.context["questions"])

    def test_index_future_posts(self):
        futureQuestion = Question(
            question_text="I am from future",
            pub_date=timezone.now() + timedelta(days=10),
        )

        nowQuestion = Question(
            question_text="I am from present", pub_date=timezone.now()
        )

        pastQuestion = Question(
            question_text="I am from past",
            pub_date=timezone.now() - timedelta(days=1),
        )

        futureQuestion.save()
        nowQuestion.save()
        pastQuestion.save()

        response = self.client.get(reverse("polls:index"))

        self.assertIs(200, response.status_code)
        self.assertQuerysetEqual(
            [nowQuestion, pastQuestion], response.context["questions"]
        )

    def test_detail_future_question(self):
        futureQuestion = Question(
            question_text="I am from future",
            pub_date=timezone.now() + timedelta(days=10),
        )
        futureQuestion.save()

        response = self.client.get(reverse("polls:detail", args=(futureQuestion.id,)))
        self.assertEqual(404, response.status_code)

    def test_detail_past_question(self):
        pastQuestion = Question(
            question_text="I am from past",
            pub_date=timezone.now() - timedelta(days=10),
        )
        pastQuestion.save()

        response = self.client.get(reverse("polls:detail", args=(pastQuestion.id,)))
        self.assertEqual(200, response.status_code)
        self.assertEqual(pastQuestion, response.context["question"])
