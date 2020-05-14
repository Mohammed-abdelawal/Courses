from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin


# Inline Admin Classes

class UnitInline(admin.TabularInline):
    model = models.Unit
    show_change_link = True
    readonly_fields = ['name', 'desc']
    ordering = ['arrange']

    def has_add_permission(self, request, obj=None):
        return False


class RelCourse(admin.TabularInline):
    model = models.Rel
    show_change_link = True
    readonly_fields = ['student', 'course', 'rel_type', 'join_date']
    ordering = ['join_date']
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

    readonly_fields = ['name', 'video', 'unit', 'host']
    ordering = ['arrange']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class QuizInline(admin.TabularInline):
    model = models.Quiz
    fieldsets = (
        (None, {
            "fields": (
                ('question', 'answer')
            ),
        }),
    )
    show_change_link = True
    can_delete = True
    extra = 0

    def has_add_permission(self, request, obj=None):
        return True


# ---------- end Inline classes


# Start Main MOdels Admin

@admin.register(models.Rel)
class RELAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'course', 'join_date', 'rel_type']
    list_filter = ['rel_type', 'course']

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or (obj is None) or (request.user is obj.course.instructor):
            return ['student', 'course']
        else:
            return ['student', 'course', 'rel_type', 'lessons_attended', 'quizzes_solved', 'rating', 'feedback', 'join_date']


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


not_staff.short_description = _('disable staff')


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    actions = [approve]
    date_hierarchy = 'pub_date'
    inlines = [UnitInline,]
    list_display = ['title', 'instructor', 'get_lessons_num', 'is_approved']
    ordering = ['pub_date']
    list_filter = ['instructor', 'category',
                   'skills_covered', 'is_approved', 'level']
    search_fields = ['title', 'skills_covered']
    filter_horizontal = ['tags', 'skills_covered']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = ((None,
                  {
                      'classes': ('extrapretty',),
                      'fields': (
                          ('instructor', 'pub_date', 'is_approved'),
                          ('title', 'slug'),
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
            list_ro += ['instructor',
                        'is_approved'] if obj.is_approved else ['instructor']
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


class CustomUserAdmin(UserAdmin):
    ordering = ('id',)
    list_display = ('email', 'is_active', 'is_staff', 'is_male')
    actions = [not_staff]
    list_filter = ('is_male', 'is_instructor')

    readonly_fields = ['pic_tag']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name','last_name')}),
        (_('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'is_instructor',
                )
            }
        ),
        (_('Additional Info'),
            {
                'fields': (
                    'about',
                    'phone',
                    'is_male',
                    'birthdate',
                    'country',
                    'city',
                    'pic',
                    'pic_tag',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


admin.site.register(models.User, CustomUserAdmin)
