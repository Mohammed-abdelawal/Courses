from django.contrib import admin
from . import views
from django.urls import path, include
from django.views.generic.base import TemplateView
# Website urls


urlpatterns = [

    # Auth Links ::

    path('register', views.RegisterView.as_view(), name='register'),
    path('accounts/', include('django.contrib.auth.urls')),

    # Static content pages ::
    path('admin/', admin.site.urls),
    path('', views.Home.as_view(), name='home'),
    path('about', views.about, name='about'),
    path('team', views.team, name='team'),

    # Navigate Courses pages ::

    path('discover/', views.discover, name='discover'),
    path('search/', views.CoursesSearchListView.as_view(), name='search'),
    path('category/<slug:category>', views.categoryCourses, name='category'),
    path('mycourses/', views.categoryCourses, name='myCourses'),

    # Overview the Course ::

    path('course/<slug:course>', views.courseView, name='course'),
    path('course/<slug:course>/<int:unit>', views.unitView, name='unit'),
    path('course/<slug:course>/<int:unit>/<int:lesson>',
         views.LessonView.as_view(), name='lesson'),

]
