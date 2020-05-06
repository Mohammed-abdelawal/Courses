from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from . import models
from django.views.generic.base import View, TemplateView
from . import forms
from django.contrib.auth import login  # , logout, authenticate
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.http import JsonResponse


# Create your views here.


def Home(request):
    print(request.user)
    return render(request, 'home.html')


def about(request):
    pass


def team(request):
    pass


class RegisterView(View):
    def post(self, request, *args, **kwargs):
        userForm = forms.UserForm(request.POST)
        profileForm = forms.ProfileForm(request.POST, request.FILES)
        if userForm.is_valid() and profileForm.is_valid():
            # hashed_password = make_password(
            #                  password=userForm.cleaned_data['password'])

            user = models.User.objects.create(
                               username=userForm.cleaned_data['username'],
                               first_name=userForm.cleaned_data['first_name'],
                               last_name=userForm.cleaned_data['last_name'],
                               email=userForm.cleaned_data['email'])

            user.set_password(userForm.cleaned_data['password'])
            # user.set_password(validated_data['password'])
            user.save()
            # user.set_password(hashed_password)
            profile = profileForm.save(False)
            profile.user = user
            if 'pic' in request.FILES:
                profile.pic = request.FILES['pic']
            profile.save()
            login(request, user)
            userForm.clean()
            profileForm.clean()
            return redirect('home')
        else:
            return render(request, 'register.html',
                          {'userForm': userForm, 'profileForm': profileForm})

    def get(self, request, *args, **kwargs):
        userForm = forms.UserForm()
        profileForm = forms.ProfileForm()

        return render(request, 'register.html', {'userForm': userForm,
                                                 'profileForm': profileForm})


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
        if course:
            c_courses.append(course)

    return render(request, 'discover.html', {'quesyset': c_courses})


class CoursesSearchView(View):

    def post(self, request, *args, **kwargs):
        return render(request, 'search.html',
                      {'SearchForm': forms.SearchForm()})

    def get(self, request, *args, **kwargs):
        form = forms.SearchForm(request.GET)

        if form.is_valid():

            if form.cleaned_data['pub_date']:
                search_c = models.Course.objects.filter(
                        name__contains=form.cleaned_data['name']).filter(
                            pub_date__gte=form.cleaned_data['pub_date'])

            else:
                search_c = models.Course.objects.filter(
                        name__contains=form.cleaned_data['name'])

            return render(request, 'search.html', {'SearchForm': form,
                                                   'queryset': search_c})
        else:
            return render(request, 'search.html', {'SearchForm': form})


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
            lesson=models.Lesson.objects.get(id=kwargs['lesson']),
            enrollment=ssc[0])
        return HttpResponse(status=200)
