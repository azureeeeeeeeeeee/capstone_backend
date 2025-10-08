from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from api.models import Faculty, ProgramStudy
from accounts.models import Role


class Command(BaseCommand):
    help = "Seed initial data for faculties, programs, and surveys"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding data..."))

        faculty_data = ["FSTI", "FPB", "FRTI"]
        faculties = [Faculty.objects.get_or_create(name=name)[0] for name in faculty_data]

        fsti = ['Matematika', 'Ilmu Aktuaria', 'Statistika', 'Fisika', 'Informatika', 'Sistem Informasi', 'Bisnis Digital', 'Teknik Elektro']
        fpb = ['Teknik Perkapalan', 'Teknik Kelautan', 'Teknik Lingkungan', 'Teknik Sipil', 'PWK', 'Arsitektur', 'DKV']
        frti = ['Teknik Mesin', 'Teknik Industri', 'Teknik Logistik', 'TMM', 'Teknologi Pangan', 'Teknik Kimia', 'Rekayasa Keselematan']

        # 2. Programs
        program_data = [
            (faculties[0], fsti),
            (faculties[1], fpb),
            (faculties[2], frti),
        ]

        total_programs = 0
        for faculty, programs in program_data:
            for name in programs:
                ProgramStudy.objects.get_or_create(faculty=faculty, name=name)
                total_programs += 1

        roles = ['Admin', 'Tracer', 'Alumni', 'Pimpinan Unit']

        for i in fsti+fpb+frti:
            roles.append(f"Prodi {i}")

        for role in roles:
            Role.objects.get_or_create(name=role)

        self.stdout.write(self.style.SUCCESS(
            f"✅ Seeding completed successfully! "
        ))