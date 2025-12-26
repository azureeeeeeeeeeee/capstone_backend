from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from api.models import (
    Survey, Section, Question, Answer,
    ProgramSpecificQuestion, SupervisorToken,
    SystemConfig
)

from accounts.models import Role

User = get_user_model()


def create_user(username, role_name, program_study=None):
    role, _ = Role.objects.get_or_create(name=role_name)
    user = User.objects.create_user(
        username=username,
        password="password123",
        role=role
    )
    if program_study:
        user.program_study = program_study
        user.save()
    return user


class SurveyAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin", "Admin")
        self.alumni = create_user("alumni", "Alumni")

        SystemConfig.objects.create(
            key="QUESTION_CODE_SPV_EMAIL",
            value="SPV_EMAIL"
        )

        self.list_url = "/api/surveys/"

    def test_get_survey_list(self):
        print("\n[Test feature] Get survey list WHEN surveys exist → expect 200 & list")

        Survey.objects.create(title="Survey 1", survey_type="lv1")
        Survey.objects.create(title="Survey 2", survey_type="skp")

        res = self.client.get(self.list_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_survey_admin(self):
        print("\n[Test feature] Create survey WHEN user is Admin → expect 201")

        self.client.force_authenticate(self.admin)

        payload = {
            "title": "Tracer Study",
            "survey_type": "lv1"
        }

        res = self.client.post(self.list_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Survey.objects.count(), 1)

    def test_create_survey_forbidden(self):
        print("\n[Test feature] Create survey WHEN user is Alumni → expect 403")

        self.client.force_authenticate(self.alumni)

        res = self.client.post(self.list_url, {
            "title": "Invalid",
            "survey_type": "lv1"
        })

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class SurveyDetailAPITest(APITestCase):
    def setUp(self):
        self.admin = create_user("admin", "Admin")
        self.survey = Survey.objects.create(
            title="Survey",
            survey_type="lv1",
            created_by=self.admin
        )
        self.url = f"/api/surveys/{self.survey.id}/"

    def test_get_detail(self):
        print("\n[Test feature] Get survey detail WHEN survey exists → expect 200")

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_update_survey(self):
        print("\n[Test feature] Update survey WHEN user is Admin → expect 200")

        self.client.force_authenticate(self.admin)

        res = self.client.patch(self.url, {"title": "Updated"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "Updated")

    def test_delete_survey(self):
        print("\n[Test feature] Delete survey WHEN user is Admin → expect 204")

        self.client.force_authenticate(self.admin)

        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, 204)


class SectionAPITest(APITestCase):
    def setUp(self):
        self.admin = create_user("admin", "Admin")
        self.client.force_authenticate(self.admin)

        self.survey = Survey.objects.create(
            title="Survey",
            survey_type="lv1",
            created_by=self.admin
        )
        self.url = f"/api/surveys/{self.survey.id}/sections/"

    def test_create_section(self):
        print("\n[Test feature] Create section WHEN user is Admin → expect 201")

        res = self.client.post(self.url, {
            "title": "Profile",
            "order": 1
        })

        self.assertEqual(res.status_code, 201)
        self.assertEqual(Section.objects.count(), 1)

    def test_get_sections(self):
        print("\n[Test feature] Get sections WHEN section exists → expect 200 & list")

        Section.objects.create(
            survey=self.survey,
            title="Profile",
            order=1
        )

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


class QuestionAPITest(APITestCase):
    def setUp(self):
        self.admin = create_user("admin", "Admin")
        self.client.force_authenticate(self.admin)

        self.survey = Survey.objects.create(
            title="Survey",
            survey_type="lv1",
            created_by=self.admin
        )
        self.section = Section.objects.create(
            survey=self.survey,
            title="Profile",
            order=1
        )

        self.url = f"/api/surveys/{self.survey.id}/sections/{self.section.id}/questions/"

    def test_create_question(self):
        print("\n[Test feature] Create question WHEN user is Admin → expect 201")

        res = self.client.post(self.url, {
            "text": "Where do you work?",
            "order": 1,
            "question_type": "text"
        })

        self.assertEqual(res.status_code, 201)
        self.assertEqual(Question.objects.count(), 1)

    def test_get_questions(self):
        print("\n[Test feature] Get questions WHEN questions exist → expect 200")

        Question.objects.create(
            section=self.section,
            text="Question",
            order=1,
            question_type="text"
        )

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)


class AnswerAPITest(APITestCase):
    def setUp(self):
        self.alumni = create_user("alumni", "Alumni")
        self.client.force_authenticate(self.alumni)

        self.survey = Survey.objects.create(title="Survey", survey_type="lv1")
        self.section = Section.objects.create(
            survey=self.survey, title="Profile", order=1
        )
        self.question = Question.objects.create(
            section=self.section,
            text="Question",
            order=1,
            question_type="text"
        )

        self.url = f"/api/surveys/{self.survey.id}/answers/"

    def test_create_answer(self):
        print("\n[Test feature] Create answer WHEN user is Alumni → expect 201")

        res = self.client.post(self.url, {
            "question": self.question.id,
            "answer_value": "Answer"
        })

        self.assertEqual(res.status_code, 201)
        self.assertEqual(Answer.objects.count(), 1)

    def test_get_answers(self):
        print("\n[Test feature] Get answers WHEN answers exist → expect 200")

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)


class SupervisorAnswerAPITest(APITestCase):
    def setUp(self):
        self.survey = Survey.objects.create(
            title="SKP",
            survey_type="skp"
        )
        self.url = f"/api/surveys/supervisor/{self.survey.id}/answers/bulk"

    def test_missing_token(self):
        print("\n[Test feature] Submit supervisor answers WHEN token is missing → expect 400")

        res = self.client.post(self.url, {"answers": []}, format="json")
        self.assertEqual(res.status_code, 400)
