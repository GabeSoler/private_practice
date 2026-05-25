from django.core.management.base import BaseCommand, CommandError
from ._create_sessions import create_sessions

class Command(BaseCommand):
    help = "adds context development (as sessions need to be on current date)"

    def add_arguments(self, parser):
        parser.add_argument("days", type=int)

    def handle(self, *args, **options):
        try:
            create_sessions(options["days"])
        except Exception as e:
            raise CommandError(f"Error creating sessions: {e}")

        self.stdout.write(
            self.style.SUCCESS('Successfully created sessions')
        )



