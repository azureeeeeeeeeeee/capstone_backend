from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from api.models import Faculty, ProgramStudy
from accounts.models import Role


class Command(BaseCommand):
    help = "Seed initial data for faculties, programs, and roles"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🌱 Seeding data..."))

        # === 1. FACULTIES ===
        faculty_data = ["FSTI", "FPB", "FRTI"]
        faculties = {}
        for name in faculty_data:
            faculty, _ = Faculty.objects.get_or_create(name=name)
            faculties[name] = faculty

        # === 2. PROGRAM STUDIES ===
        fsti = ['Matematika', 'Ilmu Aktuaria', 'Statistika', 'Fisika',
                'Informatika', 'Sistem Informasi', 'Bisnis Digital', 'Teknik Elektro']
        fpb = ['Teknik Perkapalan', 'Teknik Kelautan', 'Teknik Lingkungan',
               'Teknik Sipil', 'PWK', 'Arsitektur', 'DKV']
        frti = ['Teknik Mesin', 'Teknik Industri', 'Teknik Logistik', 'TMM',
                'Teknologi Pangan', 'Teknik Kimia', 'Rekayasa Keselematan']

        program_data = {
            "FSTI": fsti,
            "FPB": fpb,
            "FRTI": frti,
        }

        total_programs = 0
        program_mapping = {} 

        for faculty_key, programs in program_data.items():
            faculty = faculties[faculty_key]
            for name in programs:
                program, _ = ProgramStudy.objects.get_or_create(faculty=faculty, name=name)
                program_mapping[name] = program
                total_programs += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Created/Verified {total_programs} Program Studies."))

        global_roles = ['Admin', 'Tracer', 'Alumni', 'Pimpinan Unit']
        for role_name in global_roles:
            Role.objects.get_or_create(name=role_name, program_study=None)

        self.stdout.write(self.style.SUCCESS(f"✅ Created/Verified {len(global_roles)} global roles."))

        for program_name, program in program_mapping.items():
            Role.objects.get_or_create(name=f"Prodi {program_name}", program_study=program)

        self.stdout.write(self.style.SUCCESS(f"✅ Created/Verified {len(program_mapping)} program-specific roles."))

        self.stdout.write(self.style.SUCCESS("🎉 Seeding completed successfully!"))