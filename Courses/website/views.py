from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from . import models
from django.views.generic.base import View, TemplateView
from . import forms
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.http import JsonResponse

# Create your views here.


class Home(TemplateView):
    template_name = 'home.html'


def about(request):
    pass


def team(request):
    pass


class RegisterView(View):
    def post(self, request, *args, **kwargs):
        userForm = forms.UserForm(request.POST)
        profileForm = forms.ProfileForm(request.POST, request.FILES)
        if userForm.is_valid() and profileForm.is_valid():
            user = userForm.save()
            profile = profileForm.save(False)
            profile.user = user
            if 'pic' in request.FILES:
                profile.pic = request.FILES['pic']
            profile.save()
            userForm.clean()
            profileForm.clean()
            return JsonResponse({'code': 'valid'})
        else:
            errors = userForm.errors.as_ul() + profileForm.errors.as_ul()
            print(errors)
        return JsonResponse({'code': 'invalid', 'errors': errors})

    def get(self, request, *args, **kwargs):
        userForm = forms.UserForm()
        profileForm = forms.ProfileForm()

        return render(request, 'register.html', {'userForm': userForm,
                                                 'profileForm': profileForm})


def discover(request):
    categorys = models.Category.objects.only('pk')
    c_courses = []
    for cat in categorys:
        course = models.Course.objects.filter(category=cat,
                                              is_approved=True)[:5]
        if course:
            c_courses.append(course)

    return render(request, 'discover.html', {'quesyset': c_courses})


class CoursesSearchListView(ListView):
    model = models.Course
    template_name = "search.html"

    def get_queryset(self):
        pass


def categoryCourses(request, category):
    queryset = models.Course.objects.filter(category__slug=category,
                                            is_approved=True)
    return render(request, 'category.html', {'queryset': queryset})


def courseView(request, course):
    course = get_object_or_404(models.Course, slug=course, is_approved=True)
    return render(request, 'course.html', {'course': course})


def unitView(request, course, unit):
    unit = get_object_or_404(models.Unit, pk=unit, course__is_approved=True)
    return render(request, 'unit.html', {'unit': unit})


class LessonView(View):
    def get(self, request, *args, **kwargs):
        c = models.Course.objects.get(slug=kwargs['course']).pk
        sfc = models.Student_Finish_Course.objects.filter(user=request.user,
                                                          course=c)
        ssc = models.Student_Study_Course.objects.filter(user=request.user,
                                                         course=c)
        if sfc or ssc:
            l = get_object_or_404(models.Lesson, unit=kwargs['unit'],
                                  unit__course=c,
                                  pk=kwargs['lesson'])
            is_attend = models.Lesson_Attend.objects.filter(lesson=l,
                                                            enrollment=ssc[0])

            return render(request, 'lesson.html', {'lesson': l,
                          'is_attend': is_attend})

        else:
            return redirect('course', course=kwargs['course'])

    def post(self, request, *args, **kwargs):

        c = models.Course.objects.get(slug=kwargs['course']).pk
        ssc = models.Student_Study_Course.objects.filter(user=request.user,
                                                         course=c)
        person, created = models.Lesson_Attend.objects.get_or_create(
            lesson=kwargs['lesson'],
            enrollment=ssc[0])
        return HttpResponse({})
