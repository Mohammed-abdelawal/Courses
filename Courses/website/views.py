from django.contrib.auth import login  # , logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import (Http404, HttpResponse, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView, View

from . import forms, models

# Create your views here.


def Home(request):
    return render(request, 'home.html')


def about(request):
    pass


def team(request):
    pass


class RegisterView(View):
    def post(self, request, *args, **kwargs):
        if request.user.email:
            return redirect(reverse('home'))

        userForm = forms.UserForm(request.POST, request.FILES)
        if userForm.is_valid():
            user = userForm.save()
            user.set_password(userForm.cleaned_data['password'])
            if 'pic' in request.FILES:
                user.pic = request.FILES['pic']
            user.save()
            login(request, user)
            # userForm.clean()
            # profileForm.clean()
            return redirect('home')
        else:
            return render(request, 'register.html',
                          {'userForm': userForm})

    def get(self, request, *args, **kwargs):
        if request.user.email:
            return redirect(reverse('home'))

        else:
            userForm = forms.UserForm()
            return render(request, 'register.html', {'userForm': userForm})


def discover(request):
    """
        This view return list that's contain small lists inside it
        - every small list have first 5 courses or less from one category
        - access Category object in DTL with get category var in every
          first element in small list
     """
    categorys = models.Category.objects.only('pk')
    c_courses = []
    for cat in categorys:
        course = models.Course.objects.filter(category=cat,
                                              is_approved=True)[:5]
        if len(course) > 2:
            c_courses.append(course)
    return render(request, 'discover.html', {'quesyset': c_courses})


class CoursesSearchView(View):

    def get(self, request, *args, **kwargs):
        form = forms.SearchForm(request.GET)

        if form.is_valid():
            qs = models.Course.objects.all()

            return render(request, 'search.html', {'SearchForm': form,
                                                   'queryset': qs})
        else:
            print('++++++++++why not shit ?++++++++++++++')
            print(form.errors)
            return render(request, 'search.html', {'SearchForm': form})


def categoryCourses(request, category):

    queryset = get_object_or_404(models.Category, slug=category)

    return render(request, 'category.html', {'queryset': queryset})


def courseView(request, course):
    course = get_object_or_404(models.Course, slug=course, is_approved=True)
    return render(request, 'course.html', {'course': course})


@login_required
def unitView(request, course, unit):
    unit = get_object_or_404(models.Unit, pk=unit,
                             course__is_approved=True, course__slug=course)
    return render(request, 'unit.html', {'unit': unit})


class LessonView(View):
    def get(self, request, *args, **kwargs):

        lesson = get_object_or_404(models.Lesson,
                                   pk=kwargs['course'],
                                   unit__pk=kwargs['course'],
                                   unit__course__slug=kwargs['course'])

        rel = models.Rel.objects.get(student=self.request.user,
                                     course=lesson.unit.course)
        if lesson and rel:

            is_attend = rel.is_attended(l.id)

            return render(request, 'lesson.html',
                          {'lesson': l, 'is_attend': is_attend})

        else:
            return redirect('course', course=kwargs['course'])


@login_required
def attend(request, lesson_id):
    lesson = models.Lesson.get(id=lesson_id)
    course = lesson.unit.course

    rel = get_object_or_404(models.Rel,
                            student=request.user,
                            course=course)
    rel.lessons_attended.add(lesson)

    return HttpResponse({'status': 202})
