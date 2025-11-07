from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from accounts.models import CustomUser
from courses.models import Course, Enrollment


class EnrollmentAPITests(APITestCase):
    def setUp(self):
        # Users
        self.student = CustomUser.objects.create_user(
            email="student@example.com", password="pass", role="student")
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com", password="pass", role="instructor")
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com", password="pass", role="admin")

        # Course
        self.course = Course.objects.create(
            title="Test Course", slug="test-course", 
            description="desc", instructor=self.instructor, published=True)

        self.client = APIClient()

    def test_student_can_create_enrollment(self):
        self.client.force_authenticate(self.student)
        resp = self.client.post('/api/v1/enrollments/',
                                {'course': self.course.id}, format='json')
        self.assertIn(resp.status_code, (200, 201))
        self.assertTrue(Enrollment.objects.filter(
            student=self.student, course=self.course).exists())

    def test_instructor_sees_enrollments_for_their_course_in_my_enrollments(self):
        # create an enrollment first
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(self.instructor)
        resp = self.client.get('/api/v1/enrollments/my_enrollments/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.data, list)
        self.assertGreaterEqual(len(resp.data), 1)
        # course field should be present (string related field -> title)
        self.assertEqual(resp.data[0]['course'], str(self.course))

    def test_admin_can_delete_enrollment(self):
        enrollment = Enrollment.objects.create(
            student=self.student, course=self.course)
        self.client.force_authenticate(self.admin)
        resp = self.client.delete(f'/api/v1/enrollments/{enrollment.id}/')
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Enrollment.objects.filter(pk=enrollment.id).exists())
