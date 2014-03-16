from django.contrib.auth.models import User
from django.db import models
from django.contrib import admin
import pytz

from operator import itemgetter, attrgetter


LANGUAGES = (
    ('PY', 'Python'),
    ('CPP', 'C++'),
)


def make_timezones():
    data = {}
    for tz in pytz.all_timezones:
        if '/' in tz:
            area, loc = tz.split('/', 1)
        else:
            area, loc = 'Other', tz
        if area in data:
            data[area].append((tz, loc))
        else:
            data[area] = [(tz, loc)]
    data = data.items()
    data.sort(key=itemgetter(0))
    return data


TIMEZONE = make_timezones()
del make_timezones


class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name='User associated')
    name = models.CharField(max_length=50, verbose_name='Display name', null=True, blank=True)
    about = models.TextField(verbose_name='Self-description', null=True, blank=True)
    timezone = models.CharField(max_length=50, verbose_name='Timezone', default='UTC', choices=TIMEZONE)
    language = models.ForeignKey(Language, "Default language")

    def display_name(self):
        if self.name:
            return self.name
        return self.user.username

    def long_display_name(self):
        if self.name:
            return u'%s (%s)' % (self.user.username, self.name)
        return self.user.username

    def __unicode__(self):
        #return u'Profile of %s in %s speaking %s' % (self.long_display_name(), self.timezone, self.language)
        return self.long_display_name()


class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'name', 'about', 'timezone', 'language']


class ProblemType(models.Model):
    name = models.CharField(max_length=20, verbose_name='Problem category ID')
    full_name = models.CharField(max_length=100, verbose_name='Problem category name')

    def __unicode__(self):
        return self.full_name


class Problem(models.Model):
    code = models.CharField(max_length=20, verbose_name='Problem code')
    name = models.CharField(max_length=100, verbose_name='Problem name')
    description = models.TextField(verbose_name='Problem body')
    user = models.ForeignKey(Profile, verbose_name='Creator')
    types = models.ManyToManyField(ProblemType, verbose_name='Problem type')
    time_limit = models.FloatField(verbose_name='Time limit')
    memory_limit = models.FloatField(verbose_name='Memory limit')
    points = models.FloatField(verbose_name='Points')
    partial = models.BooleanField(verbose_name='Allows partial points')
    allowed_languages = models.ManyToManyField(Language, "Allowed languages")

    def types_list(self):
        return map(attrgetter('full_name'), self.types.all())

    def __unicode__(self):
        return '%s (%s), %s%s points created by %s' % (self.name, self.code, self.points, 'p' if self.partial else '',
                                                       self.user)


class Language(models.Model):
    pretty_id = models.CharField(max_length=20)
    id = models.CharField(max_length=6)


class ProblemAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('code', 'name', 'user', 'description', 'types')}),
        ('Points', {'fields': (('points', 'partial'),)}),
        ('Limits', {'fields': ('time_limit', 'memory_limit')}),
    )


class Comment(models.Model):
    user = models.ForeignKey(Profile, verbose_name='User who posted this comment')
    time = models.DateTimeField('Comment time')
    problem = models.ForeignKey(Problem, null=True, verbose_name='Associated problem')
    title = models.CharField(max_length=200, verbose_name='Title of comment')
    body = models.TextField(verbose_name='Body of comment')


class Submission(models.Model):
    user = models.ForeignKey(Profile)
    problem = models.ForeignKey(Problem)
    date = models.DateTimeField('Submission time')
    time = models.FloatField(verbose_name='Execution time', null=True)
    memory = models.FloatField(verbose_name='Memory usage', null=True)
    points = models.FloatField(verbose_name='Points granted', null=True)
    language = models.ForeignKey(Language, "Submission language")
    source = models.TextField(verbose_name='Source code')


class SubmissionTestCase(models.Model):
    parent = models.ForeignKey(Submission, verbose_name="Associated submission")
    case = models.ForeignKey(TestCase, verbose_name="Associated test case")
    status = models.IntegerField(verbose_name="Status flag")
    time = models.FloatField(verbose_name='Execution time', null=True)
    memory = models.FloatField(verbose_name='Memory usage', null=True)
    points = models.FloatField(verbose_name='Points granted', null=True)


class TestCase(models.Model):
    problem = models.ForeignKey(Problem)
    points = models.FloatField(verbose_name='Points worth', null=True)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(ProblemType)