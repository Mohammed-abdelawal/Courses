from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


# Inline Admin Classes

class UnitInline(admin.TabularInline):
    model = models.Unit
    show_change_link = True
    readonly_fields = ['name', 'desc']
    ordering = ['arrange']

    def has_add_permission(self, request, obj=None):
        return False


class FinishCourse(admin.TabularInline):
    model = models.Student_Finish_Course
    show_change_link = True
    readonly_fields = ['user', 'course', 'rating', 'feedback', 'date']
    ordering = ['date']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class StudyCourse(admin.TabularInline):
    model = models.Student_Study_Course
    show_change_link = True
    readonly_fields = ['user', 'course', 'date']
    ordering = ['date']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class Lesson_AttendInline(admin.TabularInline):
    model = models.Lesson_Attend
    show_change_link = True
    readonly_fields = ['lesson', 'enrollment']
    ordering = ['lesson__arrange']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class Quiz_SolveInline(admin.TabularInline):
    model = models.Quiz_Solve
    show_change_link = True
    readonly_fields = ['quiz', 'enrollment', 'is_True']
    ordering = ['enrollment']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class LessonInline(admin.TabularInline):
    model = models.Lesson
    show_change_link = True
    fieldsets = (
        (None, {
            "fields": (
                'name', 'video', 'arrange', 'unit', 'host'
            ),
        }),
    )
    
    readonly_fields = ['name','video','unit','host']
    ordering = ['arrange']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class QuizInline(admin.TabularInline):
    model = models.Quiz
    fieldsets = (
        (None, {
            "fields": (
                ('question', 'style', 'answer')
            ),
        }),
    )
    show_change_link = True
    readonly_fields = ['question', 'style', 'answer']
    can_delete = False
    def has_add_permission(self, request, obj=None):
        return False


# ---------- end Inline classes


# Start Main MOdels Admin


@admin.register(models.Student_Study_Course)
class StudyCourseAdmin(admin.ModelAdmin):
    inlines = [Quiz_SolveInline, Lesson_AttendInline]
    list_display = ['id', 'user', 'course', 'date']
    list_filter = ['date', 'course']

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or (obj is None ) or (request.user is obj.course.instructor):
            return []
        else:
            return ['user', 'course']


@admin.register(models.Unit)
class UnitAdmin(admin.ModelAdmin):
    inlines = [LessonInline, QuizInline]
    exclude = ['arrange']
    search_fields = ['name', 'desc']
    list_filter = ['course']
    list_display = ['id', 'name', 'course']
    fieldsets = (
        (None, {
            "fields": (
                'course', 'name', 'desc'
            ),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        return ['course'] if obj else []


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
    list_filter = ['instructor', 'category', 'skills_covered', 'is_approved', 'level']
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
    list_display_links = ['id', 'name']
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display_links = ['id', 'name']
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display_links = ['id', 'name']
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display_links = ['id', 'name']
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(models.Host)
class HostAdmin(admin.ModelAdmin):
    list_display_links = ['id', 'name']
    list_display = ['id', 'name', 'website']
    search_fields = ['name']


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(models.NewsTeller)
class NewsTellerAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'is_subscribe']
    search_fields = ['email']
    list_display_links = ['id', 'email']

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        elif obj:
            return ['is_subscribe', 'email']
        else:
            return['is_subscribe']


@admin.register(models.NewsTeller_Emails)
class NewsTeller_EmailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject']
    search_fields = ['subject']
    list_display_links = ['id', 'subject']

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or not obj:
            return []
        else:
            return ['subject', 'msg']


@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'unit']
    search_fields = ['name', 'desc']
    list_display_links = ['id', 'name']
    exclude = ['arrange']

    def get_readonly_fields(self, request, obj=None):
        ro = ['unit']
        if request.user.is_superuser:
            return ro
        elif obj and obj.unit.course.instructor is request.user:
            return ro
        elif not obj:
            return []
        else:
            return ro+['name', 'video', 'host', 'text']


# Custom user to add profile model


def NOT_STAFF(modeladmin, request, queryset):
    if request.user.is_superuser:
        queryset.update(is_staff=False)
not_staff.short_description = _('desactive staff')


def SEND_EMAIL(modeladmin, request, queryset):
    print('Send Email')
SEND_EMAIL.short_description = _('Send Email')


class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False
    verbose_name = 'Profile'
    fk_name = 'user'
    radio_fields = {'is_male': admin.HORIZONTAL}


class CustomUserAdmin(UserAdmin):
    UserAdmin.list_display += ('is_active',)
    inlines = [ProfileInline, FinishCourse, StudyCourse]
    UserAdmin.actions += [not_staff]
    UserAdmin.list_filter += ('profile__is_male',)

    # UserAdmin.list_display += ('username',)

admin.site.unregister(models.User)
admin.site.register(models.User, CustomUserAdmin)
