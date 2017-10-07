from autofixture import AutoFixture
from django.core.management.base import BaseCommand, CommandError
from polls.models import Poll


class Command(BaseCommand):
    help = 'Creates some demo Polls'

    def handle(self, *args, **options):
        NUMBER_OF_AUTO_POLLS = 10
        fixture = AutoFixture(Poll)
        fixture.create(NUMBER_OF_AUTO_POLLS, True)
        Poll.objects.create(title='Hello World DRQ!')
        self.stdout.write(self.style.SUCCESS('Successfully created %s polls' % (NUMBER_OF_AUTO_POLLS + 1)))
