from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.views import View
from rest_framework import generics, mixins, status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import QuestionForm, SignUpForm
from .models import Choice, Question
from .serializers import QuestionSerializer


@api_view(["GET"])
# @authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def api_index(request):
    print(request.user.username)
    questions = Question.objects.all()
    serializer = QuestionSerializer(questions, many=True)

    return Response(serializer.data, status=418)


@api_view(["POST"])
def api_post(request):
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        question = serializer.save()
        return Response({"detail": "save success", "question_id": question.id})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'PUT', 'DELETE'])
# def api_question_detail(request, pk):
#    try:
#        question = Question.objects.get(pk=pk)
#    except Question.DoesNotExist:
#        return Response(status=status.HTTP_404_NOT_FOUND)

#    if request.method == 'GET':
#        serializer = QuestionSerializer(question)
#        return Response(serializer.data)

#    elif request.method == 'PUT':
#        serializer = QuestionSerializer(question, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#    elif request.method == 'DELETE':
#        question.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)

# class QuestionDetailView(APIView):
#     def get_object(self, pk):
#        try:
#            return Question.objects.get(pk=pk)
#        except Question.DoesNotExist:
#            return None

#     def get(self, request, pk):
#         question = self.get_object(pk)
#         if question is None:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         serializer = QuestionSerializer(question)
#         return Response(serializer.data)
    
#     def put(self, request):
#         return Response({})
    
#     def delete(self, request):
#         return Response({})

# class QuestionDetailView(mixins.RetrieveModelMixin,
#                          mixins.UpdateModelMixin,
#                          mixins.DestroyModelMixin,
#                          generics.GenericAPIView):
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

#     def put(self, request, *args, **kwargs):
#         return self.update(request,*args, **kwargs)

#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request,*args, **kwargs)

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

# class QuestionList(mixins.ListModelMixin,
#                   mixins.CreateModelMixin,
#                   generics.GenericAPIView):
#    queryset = Question.objects.all()
#    serializer_class = QuestionSerializer

#    def get(self, request, *args, **kwargs):
#        return self.list(request, *args, **kwargs)

#    def post(self, request, *args, **kwargs):
#        return self.create(request, *args, **kwargs)

class QuestionList(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


@login_required(login_url="/login/")
def index(request):
    questions = (
        Question.objects.filter(pub_date__lte=timezone.now())
        .order_by("-pub_date")
        .all()
    )
    context = {"questions": questions}
    return render(request, "polls/index.html", context)


# Create your views here.
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id, pub_date__lte=timezone.now())
    context = {"question": question}
    return render(request, "polls/detail.html", context)


def vote(request, question_id):
    choice_id = int(request.POST["choice"][0])

    choice = get_object_or_404(Choice, pk=choice_id)
    choice.votes += 1
    choice.save()
    return HttpResponseRedirect(reverse("polls:results", args=(question_id,)))


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    context = {"question": question}
    return render(request, "polls/results.html", context)


@login_required(login_url="/login/")
@permission_required("polls.add_question", login_url="/login/")
def add_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            return HttpResponseRedirect(reverse("polls:index"))
    else:
        form = QuestionForm()
    return render(request, "polls/question.html", {"form": form})


class QuestionEditView(View):
    def get(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id)
        form = QuestionForm(instance=question)
        return render(
            request,
            "polls/question_edit.html",
            {"form": form, "question_id": question_id},
        )

    def post(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id)

        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("polls:detail", args=(question_id,)))


def sign_up(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            # добавить в default
            group = Group.objects.get(name="default")
            group.user_set.add(user)

            login(request, user)
            return redirect(reverse("polls:index"))
    else:
        form = SignUpForm()

    return render(request, "registration/sign_up.html", {"form": form})


def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        if request.user == question.author or request.user.has_perm(
            "polls.delete_question"
        ):
            question.delete()
    return redirect(reverse("polls:index"))
