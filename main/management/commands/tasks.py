from django.core.management.base import BaseCommand, CommandError
from AioTest.models import CarMark, CarModel
from django_cron import CronJobBase, Schedule
