import os
import uuid

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.html import format_html
# --- HELPER FUNCTIONS ---


def birth_validator(birthdate):
    if int(birthdate.year) > (timezone.now().year - 7):
        raise ValidationError(_("""you can\'t create account 
                                if you are Younger than 7 Years """))


def uuid_path(instance, file_name):
    """Generate file name with uuid"""
    ext = file_name.split('.')[-1]
    file_name = f'{uuid.uuid4()}.{ext}'
    return os.path.join('pp', file_name)

# --- User Model ---


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new User"""
        if not email:
            raise ValueError(_('User should have E-mail address'))
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """ Create Super user for testing things """
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""

    email = models.EmailField(_('Email'), max_length=255, unique=True)
    first_name = models.CharField(_('First Name'), max_length=255)
    last_name = models.CharField(_('Last Name'), max_length=255)
    is_active = models.BooleanField(_('Is Active ?'), default=True)
    is_staff = models.BooleanField(_('Is Staff ?'), default=False)
    is_instructor = models.BooleanField(_('Is Instructor ?'), default=False)
    about = models.TextField(_('Description'), null=True, blank=True)
    phone = models.CharField(_('Phone'), max_length=20, blank=True, null=True)
    is_male = models.BooleanField(_('Gender'), default=True,
                                  choices=((True, _('Male')), (False, _('Female'))))
    birthdate = models.DateField(verbose_name=_('Birth date'), null=True,
                                 blank=True, validators=[birth_validator])
    country = models.CharField(_('Country'), max_length=30, blank=True, null=True)
    city = models.CharField(_('City'), max_length=30, blank=True, null=True)
    pic = models.ImageField(_('Personal Pic'), upload_to=uuid_path,
                            null=True, blank=True)
    courses = models.ManyToManyField(
        'Course', through='Rel', related_name='students')

    objects = UserManager()
    USERNAME_FIELD = 'email'

    def pic_tag(self):
        return format_html('<img src="{}" width="450px" />'.format(self.pic.url))
    pic_tag.short_description = _('Image')
    pic_tag.allow_tags = True

    def __str__(self):
        return self.first_name


class Skill(models.Model):
    name = models.CharField(_('Skill name'), max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')


class Host(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    website = models.URLField(_('Website'), max_length=200)
    after = models.TextField(_('After Link'))
    before = models.TextField(_('Before Link'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Host')
        verbose_name_plural = _('Hosts')


class Language(models.Model):
    name = models.CharField(_('Language'), unique=True,
                            help_text=_('CAPITAL chars'),
                            max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')


class Level(models.Model):
    name = models.CharField(_('Level'), unique=True,
                            help_text=_('Level name'),
                            max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Level')
        verbose_name_plural = _('Levels')


class Category(models.Model):
    name = models.CharField(_('Category name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug in url'), unique=True)
    desc = models.TextField(_('Description'))
    
    def get_5_courses(self):
        return self.courses.filter(is_approved=True)[:5]
    
    def get_courses(self):
        return self.courses.filter(is_approved=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class Tag(models.Model):
    name = models.CharField(verbose_name=_('Tag Name'),
                            max_length=50, unique=True)
    desc = models.TextField(verbose_name=_('Description'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')


class Course(models.Model):
    """This Model Describe Course data"""
    slug = models.SlugField(_('slug for url'), unique=True)
    instructor = models.ForeignKey(verbose_name=_('The Instructor'),
                                   to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   limit_choices_to={'is_instructor': True},
                                   related_name='courses_instructor')
    title = models.CharField(_('Title'), max_length=255)
    category = models.ForeignKey(verbose_name=_('Category'),
                                 to='Category', on_delete=models.PROTECT,
                                 related_name='courses')
    tags = models.ManyToManyField(verbose_name=_('Tags'), to=Tag,
                                  related_name='courses')
    time = models.IntegerField(verbose_name=_('Full course time in Hours'))
    pub_date = models.DateTimeField(_('Publish Date'), null=True,
                                    blank=True, default=None)
    files = models.FileField(_("""Attached Files in Zip and named
                               as course title"""), null=True,
                             blank=True, upload_to='CF')
    is_approved = models.BooleanField(verbose_name=_('Is Approved By Admin ?'),
                                      default=False)

    # Fields for help student to know more about course

    skills_covered = models.ManyToManyField(to=Skill, related_name='courses',
                                            verbose_name=_('Skiils Covered in Course'))
    intro_text = models.TextField(_('Course Text introduction'))
    intro_video = models.URLField(_('introduction video'),
                                  help_text=_('This should be embed YouTube link'))
    before = models.TextField(_('Before the course'),
                              help_text=_('What student should know '
                                          'about before enroll in course'))
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
        return self.title

    def get_lessons_num(self):
        i = 0
        for d in Unit.objects.filter(course=self.pk):
            i += d.get_lessons_num()
        return i
    get_lessons_num.short_description = _('Lessons Number')

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
                               related_name='units')
    desc = models.TextField(verbose_name=_('Description'))
    arrange = models.IntegerField(verbose_name=_('Unit Arrange'), validators=[
        MinValueValidator(1, _('Arrange start at \'1\''))], default=1)

    class Meta:
        verbose_name = _('Unit')
        verbose_name_plural = _('Units')
        unique_together = [['arrange', 'course']]

    def __str__(self):
        return self.name

    def get_lessons_num(self):
        return Lesson.objects.filter(unit=self.pk).count()


class Quiz(models.Model):
    unit = models.ForeignKey(to=Unit, on_delete=models.CASCADE,
                             verbose_name=_('Unit'),
                             related_name='quizzes')
    question = models.CharField(_('Choice Question'), max_length=255)
    answer = models.CharField(_('True answer'), max_length=255)
    ch1 = models.CharField(_('False 1'), max_length=255,
                           null=True, blank=True)
    ch2 = models.CharField(_('False 2'), max_length=255,
                           null=True, blank=True)
    ch3 = models.CharField(_('False 3'), max_length=255,
                           null=True, blank=True)
    ch4 = models.CharField(_('False 4'), max_length=255,
                           null=True, blank=True)

    def check_answer(self, answer):
        return (str(answer).lower() == str(self.answer).lower())

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')


class Lesson(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    text = models.TextField(_('Lesson Text'))
    video = models.URLField(_('Video Link'),
                            help_text=_('embeded video link'))
    arrange = models.IntegerField(_('Arrange in Unit'), default=1,
                                  validators=[MinValueValidator(1, _('Arrange start at \'1\''))])
    unit = models.ForeignKey(verbose_name=_('Unit'), to=Unit,
                             on_delete=models.CASCADE,
                             related_name='lessons')
    host = models.ForeignKey(Host, verbose_name=_('Host'),
                             on_delete=models.PROTECT)

    def __str__(self):
        return self.name + ' unit : ' + self.unit.name

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        unique_together = [['arrange', 'unit']]


class Rel(models.Model):
    """describe and implement all relation
    types and interactions between Student and course"""
    ENROLLMENT = 1
    FINISHED = 2
    TYPE_CHOICES = (
        (ENROLLMENT, _('ENROLLMENT')),
        (FINISHED, _('FINISHED')),
    )

    course = models.ForeignKey(
        'Course', related_name='details', on_delete=models.PROTECT)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='details', on_delete=models.CASCADE)
    rel_type = models.IntegerField(choices=TYPE_CHOICES, default=ENROLLMENT)
    lessons_attended = models.ManyToManyField('Lesson', related_name='attend')
    quizzes_solved = models.ManyToManyField('Quiz', related_name='solve')
    rating = models.IntegerField(_('Rating'), blank=True, null=True,
                                 validators=(MinValueValidator(0), MaxValueValidator(10)))
    feedback = models.CharField(
        _('Review'), max_length=255, blank=True, null=True)
    join_date = models.DateTimeField(_('Join Date'), auto_now_add=True)

    def is_attended(self, lesson_id):
        return self.lessons_attended.filter(pk=lesson_id).exists()

    def __str__(self):
        return str(self.course) + ' ' + str(self.student)
    
    class Meta:
        unique_together = [['course', 'student']]



class NewsTeller(models.Model):
    email = models.EmailField(verbose_name=_('Email'), unique=True)
    is_subscribe = models.BooleanField(verbose_name=_('is Subscribe'),
                                       default=True)

    class Meta:
        verbose_name = _('News Teller Subscriber')
        verbose_name_plural = _('NewsTeller Subscriber')


class NewsTeller_Emails(models.Model):
    msg = models.TextField(verbose_name=_('MSG'))
    subject = models.CharField(verbose_name=_('Subject'), max_length=100)

    class Meta:
        verbose_name = _('NewsTeller Email')
        verbose_name_plural = _('NewsTeller Emails')
