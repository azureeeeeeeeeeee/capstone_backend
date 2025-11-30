from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from api.models import Faculty, ProgramStudy, Department, SystemConfig
from accounts.models import Role, User


class Command(BaseCommand):
    help = "Seed initial data for faculties, programs, and roles"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🌱 Seeding data..."))

        faculty_data = ["Fakultas Sains dan Teknologi Informasi", "Fakultas Pembangunan Berkelanjutan", "Fakultas Rekayasa dan Teknologi Industri"]
        faculties = {}
        for name in faculty_data:
            faculty, _ = Faculty.objects.get_or_create(name=name)
            faculties[name] = faculty

        self.stdout.write(self.style.SUCCESS(f"Seeded Faculties into DB !."))

        # fakultas -> jurusan
        department_data = {
            "Fakultas Sains dan Teknologi Informasi": ["Jurusan Sains dan Analitika Data", "Jurusan Teknik Elektro, Informatika, dan Bisnis"],
            "Fakultas Pembangunan Berkelanjutan": ["Jurusan Teknologi Kemaritiman", "Jurusan Teknik Sipil dan Perencanaan"],
            "Fakultas Rekayasa dan Teknologi Industri": ["Jurusan Teknologi Industri", "Jurusan Rekayasa Industri"],
        }

        departments = {}

        for faculty_name, dept_list in department_data.items():
            faculty = faculties[faculty_name]
            for dept_name in dept_list:
                dept, _ = Department.objects.get_or_create(
                    name=dept_name,
                    faculty=faculty
                )
                departments[dept_name] = dept

        self.stdout.write(self.style.SUCCESS(f"Seeded Department into DB !."))



        # jurusan -> prodi
        # jsad = ["Matematika", "Ilmu Aktuaria", "Statistika", "Fisika"]
        # jteib = ["Informatika", "Sistem Informasi", "Bisnis Digital", "Teknik Elektro"]

        # jtk = ["Teknik Perkapalan", "Teknik Kelautan", "Teknik Lingkungan"]
        # jtsp = ["Teknik Sipil", "Perencanaan Wilayah dan Kota", "Arsitektur", "Desain Komunikasi Visual"]

        # jti = ["Teknik Mesin", "Teknik Industri", "Teknik Logistik", "Teknik Material dan Metalurgi"]
        # jri = ["Teknologi Pangan", "Teknik Kimia", "Rekayasa Keselamatan"]

        program_data = {
            "Jurusan Sains dan Analitika Data": [
                "Matematika", "Ilmu Aktuaria", "Statistika", "Fisika"
            ],
            "Jurusan Teknik Elektro, Informatika, dan Bisnis": [
                "Informatika", "Sistem Informasi", "Bisnis Digital", "Teknik Elektro"
            ],
            "Jurusan Teknologi Kemaritiman": [
                "Teknik Perkapalan", "Teknik Kelautan", "Teknik Lingkungan"
            ],
            "Jurusan Teknik Sipil dan Perencanaan": [
                "Teknik Sipil", "Perencanaan Wilayah dan Kota",
                "Arsitektur", "Desain Komunikasi Visual"
            ],
            "Jurusan Teknologi Industri": [
                "Teknik Mesin", "Teknik Industri",
                "Teknik Logistik", "Teknik Material dan Metalurgi"
            ],
            "Jurusan Rekayasa Industri": [
                "Teknologi Pangan", "Teknik Kimia", 
                "Rekayasa Keselamatan"
            ],
        }

        program_mapping = {}

        for dept_name, prodi_list in program_data.items():
            dept = departments[dept_name]
            for prodi in prodi_list:
                program, _ = ProgramStudy.objects.get_or_create(
                    department=dept,
                    name=prodi
                )
                program_mapping[prodi] = program


        self.stdout.write(self.style.SUCCESS(f"Seeded Program Studies into DB !."))

        global_roles = ['Admin', 'Tracer', 'Alumni', 'Pimpinan Unit']
        for role_name in global_roles:
            Role.objects.get_or_create(name=role_name, program_study=None)

        self.stdout.write(self.style.SUCCESS(f"Seeded global roles into DB."))

        for program_name, program in program_mapping.items():
            Role.objects.get_or_create(name=f"Prodi {program_name}", program_study=program)

        self.stdout.write(self.style.SUCCESS(f"Seeded program-specific roles."))


        admin_role = Role.objects.get(name="Admin")

        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "id": "admin tracer",
                "username": "Admin Tracer Study",
                "email": "admin@example.com",
                "role": admin_role,
            }
        )

        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Default admin user created: admin / admin123"))
        else:
            self.stdout.write(self.style.WARNING("Admin user already exists, skipped."))


        SystemConfig.objects.get_or_create(key="QUESTION_CODE_SPV_EMAIL", value="SPV_02")

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully!"))