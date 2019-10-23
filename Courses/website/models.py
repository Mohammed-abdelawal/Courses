from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


# Validators


def birth_validator(birthdate):
    if int(birthdate.year) > (timezone.now().year - 7):
        raise ValidationError(_('you can\'t create account '
                              'if you are Younger than 7 Years '))


# --------- Models ---------


class Skill(models.Model):
    name = models.CharField(verbose_name=_('Skill name'), max_length=120)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')


class Profile(models.Model):
    ''' this model to store more efficient data about our users
        - it connect with django user model with (user) field
    '''
    user = models.OneToOneField(verbose_name=_('The User'), to=User,
                                on_delete=models.CASCADE)
    about = models.TextField(verbose_name=_('Description'), null=True,
                             max_length=2000, blank=True)
    phone = models.CharField(verbose_name=_('Phone'), max_length=20)
    is_male = models.BooleanField(verbose_name=_('Gender'), choices=(
        (False, _('Male')),
        (True, _('Female'))))
    birthdate = models.DateField(verbose_name=_('Birth date'), null=True,
                                 blank=True, validators=[birth_validator])
    country = models.CharField(verbose_name=_('Country'), max_length=30)
    city = models.CharField(verbose_name=_('City'), max_length=30)
    state = models.CharField(verbose_name=_('state'), max_length=30,
                             blank=True, null=True)
    saved = models.ManyToManyField(verbose_name=_('Saved courses'), blank=True,
                                   to='Course', related_name='like')
    pic = models.ImageField(verbose_name=_('Personal Pic'), upload_to='PP',
                            null=True, blank=True)

    def __str__(self):
        return self.user.__str__()

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')


'''
class Instructor(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
'''


class Language(models.Model):
    name = models.CharField(help_text=_('CAPITAL chars'),
                            verbose_name=_('Language'),
                            max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')


class Level(models.Model):
    name = models.CharField(help_text=_('Level name'),
                            verbose_name=_('Level'),
                            max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Level')
        verbose_name_plural = _('Levels')


class Category(models.Model):
    name = models.CharField(verbose_name=_('Category name'), max_length=100)
    slug = models.SlugField(verbose_name=_('slug in url'), unique=True)
    desc = models.TextField(verbose_name=_('Description'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class Tag(models.Model):
    name = models.CharField(verbose_name=_('Tag Name'), max_length=50)
    desc = models.TextField(verbose_name=_('Description'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')


class Course(models.Model):
    ''' This Model Describe Course data'''
    slug = models.SlugField(verbose_name=_('slug in url'), unique=True)
    instructor = models.ForeignKey(verbose_name=_('The Instructor'),
                                   to=User, on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('The Name'), max_length=150)
    category = models.ForeignKey(verbose_name=_('Category'),
                                 to='Category', on_delete=models.PROTECT)
    tags = models.ManyToManyField(verbose_name=_('Tags'), to=Tag,
                                  related_name='Ctags')
    time = models.IntegerField(verbose_name=_('Full course time in Hours'))
    pub_date = models.DateField(verbose_name=_('Publish Date'), null=True,
                                blank=True, default=None)
    expiration_date = models.DateField(verbose_name=_('Expiration Date'),
                                       null=True, blank=True)
    files = models.FileField(verbose_name=_('Attached Files in Zip and named '
                             'as course title'), null=True, blank=True,
                             upload_to='CF')
    is_approved = models.BooleanField(verbose_name=_('Is Approved By Admin ?'),
                                      default=False)

    # Fields for help student to know more about course

    skills_covered = models.ManyToManyField(to=Skill, related_name='skill',
                                            verbose_name=_('Skiils Covered '
                                                           'in Course'))
    intro_text = models.TextField(verbose_name=_('Course Text introduction'))
    intro_video = models.URLField(verbose_name=_('introduction video'),
                                  help_text=_('This should be embed YouTube'))
    before = models.TextField(verbose_name=_('Before the course'),
                              help_text=_('What student should '
                              'know about before enroll in course'))
    after = models.TextField(verbose_name=_('After the course'),
                             help_text=_('What student can do after'))

    # Fields below is for better classification

    language = models.ForeignKey(to=Language, on_delete=models.PROTECT,
                                 verbose_name=_('Language'),
                                 blank=True, null=True)
    level = models.ForeignKey(to=Level, on_delete=models.PROTECT,
                              verbose_name=_('Level'),
                              blank=True, null=True)

    def __str__(self):
        return self.name

    def get_lessons_num(self):
        i = 0
        for d in Unit.objects.filter(course=self.pk):
            i += d.get_v_num()
        return i
    get_lessons_num.short_description = _('Lesson count')

    def get_units_num(self):
        return Unit.objects.filter(course=self.pk).count()

    def save(self, *args, **kwargs):
        if (self.is_approved) and (self.pub_date is None):
            self.pub_date = timezone.now()
        super(Course, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['pub_date']


class Unit(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('The name'))
    course = models.ForeignKey(verbose_name=_('Course'), to=Course,
                               on_delete=models.CASCADE,
                               related_name='course_unit')
    desc = models.TextField(verbose_name=_('Description'))
    arrange = models.IntegerField(verbose_name=_('Unit Arrange'), validators=[
        MinValueValidator(1, _('Arrange start at \'1\''))], default=0)

    class Meta:
        verbose_name = _('Unit')
        verbose_name_plural = _('Units')
        unique_together = [['arrange', 'course']]

    def __str__(self):
        return self.name

    def get_v_num(self):
        return len(Lesson.objects.filter(unit=self.pk))


class Quiz(models.Model):
    unit = models.ForeignKey(to=Unit, on_delete=models.CASCADE,
                             verbose_name=_('Unit'),
                             related_name='unit_quiz')
    question = models.CharField(verbose_name=_('Question'), max_length=200)
    style = models.IntegerField(verbose_name=_('style'), default=1,
                                choices=((0, _('Choose')),
                                         (1, _('Complete')),
                                         (2, _('Check Done'))))
    answer = models.CharField(verbose_name=_('True answer'), max_length=200)
    ch1 = models.CharField(verbose_name=_('False 1'), max_length=200,
                           null=True, blank=True)
    ch2 = models.CharField(verbose_name=_('False 2'), max_length=200,
                           null=True, blank=True)
    ch3 = models.CharField(verbose_name=_('False 3'), max_length=200,
                           null=True, blank=True)

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')

    def __str__(self):
        return self.question


class Lesson(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=60)
    text = models.TextField(verbose_name=_('Lesson Text'))
    video = models.URLField(verbose_name=_('Video Link'),
                            help_text=_('embeded video link'))
    arrange = models.IntegerField(verbose_name=_('Arrange in Unit'),
                                  validators=[
                            MinValueValidator(1, _('Arrange start at \'1\''))])
    unit = models.ForeignKey(verbose_name=_('Unit'), to=Unit,
                             on_delete=models.CASCADE,
                             related_name='unit_lesson')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        unique_together = [['arrange', 'unit']]


class Quiz_Solve(models.Model):
    quiz = models.ForeignKey(to=Quiz, on_delete=models.CASCADE,
                             verbose_name=_('quiz'))
    enrollment = models.ForeignKey(to='Student_Study_Course',
                                   on_delete=models.CASCADE,
                                   verbose_name=_('enrollment'),
                                   related_name='enroll_quiz')
    is_True = models.BooleanField(verbose_name=_('is True?'))

    class Meta:
        verbose_name = _("Quiz_Solve")
        verbose_name_plural = _("Quizs_Solves")
        unique_together = [['quiz', 'enrollment']]

    def __str__(self):
        return str(self.quiz) + ' ' + str(self.is_True)

    def clean(self):
        e_c = Student_Study_Course.objects.get(pk=self.enrollment.pk).course
        q_c = Unit.objects.get(unit_quiz=self.quiz).course
        if q_c.pk != e_c.pk:
            raise ValidationError(_('The Quiz ('+str(self.quiz) +
                                    ') not in this course'))


class Lesson_Attend(models.Model):
    lesson = models.ForeignKey(to=Lesson, on_delete=models.CASCADE,
                               verbose_name=_('lesson'),
                               related_name='lesson_attend')
    enrollment = models.ForeignKey(to='Student_Study_Course',
                                   on_delete=models.CASCADE,
                                   verbose_name=_('enrollment'),
                                   related_name='enroll_lesson')

    class Meta:
        verbose_name = _("Attended Lesson")
        verbose_name_plural = _("Attended Lessons")
        unique_together = [['lesson', 'enrollment']]

    def __str__(self):
        return str(self.lesson)

    def clean(self):
        e_c = Student_Study_Course.objects.get(pk=self.enrollment.pk).course
        l_c = Unit.objects.get(unit_lesson=self.lesson).course
        if l_c.pk != e_c.pk:
            raise ValidationError(_('The Lesson ('+str(self.lesson) +
                                    ')not in this course'))


class Student_Study_Course(models.Model):
    user = models.ForeignKey(verbose_name=_('User'), to=User,
                             on_delete=models.CASCADE,
                             related_name='course_study')
    course = models.ForeignKey(verbose_name=_('Course'), to=Course,
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        unique_together = [['user', 'course']]

    def __str__(self):
        return str(self.pk) + '-' + str(self.user)+' - '+str(self.course)


class Student_Finish_Course(models.Model):
    user = models.ForeignKey(verbose_name=_('User'), to=User,
                             on_delete=models.CASCADE)
    course = models.ForeignKey(verbose_name=_('Course'), to=Course,
                               on_delete=models.CASCADE,
                               related_name='course_finish')
    rating = models.IntegerField(verbose_name=_('Rating'),
                                 validators=[MinValueValidator(0),
                                             MaxValueValidator(10)])
    feedback = models.TextField(verbose_name=_('Course FeedBack'))
    date = models.DateField(verbose_name=_('Date'), auto_now_add=True)

    class Meta:
        verbose_name = _('Finished Enrolls')
        verbose_name_plural = _('Finished Enrolls')
        unique_together = [['user', 'course']]
