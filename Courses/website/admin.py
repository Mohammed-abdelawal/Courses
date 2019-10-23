from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


# Register your models here.


class FinishCourse(admin.TabularInline):
    model = models.Student_Finish_Course
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return ['user', 'course', 'rating', 'feedback', 'date']


class StudyCourse(admin.TabularInline):
    model = models.Student_Study_Course
    extra = 1
    show_change_link = True

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return ['user', 'course']


class Lesson_AttendInline(admin.TabularInline):
    model = models.Lesson_Attend
    extra = 1


class Quiz_SolveInline(admin.TabularInline):
    model = models.Quiz_Solve
    extra = 1


@admin.register(models.Student_Study_Course)
class StudyCourseAdmin(admin.ModelAdmin):
    inlines = [Quiz_SolveInline, Lesson_AttendInline]

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        if obj and (request.user is obj.course__instructor):
            return []
        else:
            return ['user', 'course']


class LessonInline(admin.StackedInline):
    model = models.Lesson
    extra = 1


class QuizInline(admin.StackedInline):
    model = models.Quiz
    fieldsets = (
        (None, {
            "fields": (
                ('question', 'style', 'answer'),
                ('ch1', 'ch2', 'ch3')
            ),
        }),
    )
    extra = 1


@admin.register(models.Unit)
class UnitAdmin(admin.ModelAdmin):
    inlines = [LessonInline, QuizInline]
    exclude = ['arrange']


class UnitInline(admin.StackedInline):
    model = models.Unit
    extra = 0
    show_change_link = True


def approve(modeladmin, request, queryset):
    queryset.update(is_approved=True)
approve.short_description = _('Approve Course')


def not_staff(modeladmin, request, queryset):
    if request.user.is_superuser:
        queryset.update(is_staff=False)
not_staff.short_description = _('disabled staff')


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    actions = [approve]
    date_hierarchy = 'pub_date'
    inlines = [UnitInline, StudyCourse, FinishCourse]
    list_display = ['name', 'instructor', 'get_lessons_num', 'is_approved']
    ordering = ['pub_date']
    list_filter = ['instructor', 'category', 'skills_covered', 'is_approved']
    search_fields = ['name', 'skills_covered']
    filter_horizontal = ['tags', 'skills_covered']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = ((None,
                 {
                   'classes': ('extrapretty',),
                   'fields': (
                             ('instructor', 'pub_date', 'is_approved'),
                             ('name', 'slug'),
                             'time', 'files', (),
                             ('language', 'level', 'category'),
                             ('tags', 'skills_covered'),
                             'intro_text', 'intro_video',
                             'after', 'before', ()
                             )
                 },),)

    def get_readonly_fields(self, request, obj=None):
        list_ro = ['pub_date']
        if obj:
            list_ro += ['instructor', 'is_approved'] if obj.is_approved else ['instructor']
        else:
            list_ro += ['is_approved']

        if request.user.is_superuser:
            return []
        return list_ro


@admin.register(models.Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


# Custom user to add profile model


def not_staff(modeladmin, request, queryset):
    if request.user.is_superuser:
        queryset.update(is_staff=False)
not_staff.short_description = _('desactive staff')


class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False
    verbose_name = 'Profile'
    fk_name = 'user'
    radio_fields = {'is_male': admin.HORIZONTAL}


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline, FinishCourse, StudyCourse]
    UserAdmin.actions += [not_staff]

    # UserAdmin.list_display += ('username',)

admin.site.unregister(models.User)
admin.site.register(models.User, CustomUserAdmin)
