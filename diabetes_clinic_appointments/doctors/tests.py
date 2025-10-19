"""
Tests for Doctor model.
"""

from django.test import TestCase
from django.db import IntegrityError
from datetime import time
from authentication.models import User
from doctors.models import Doctor


class DoctorCreationTest(TestCase):
    """Test Doctor model creation"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='doctor1',
            password='testpass123',
            user_type='doctor',
            first_name='Anna',
            last_name='Nowak'
        )

    def test_create_doctor(self):
        """Test creating a doctor"""
        doctor = Doctor.objects.create(
            user=self.user,
            license_number='DOC12345',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Lekarska 5, Warszawa',
            consultation_fee=250.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            working_days='mon-fri',
            education='Medical University of Warsaw',
            certifications='Diabetes Specialist Certification',
            bio='Experienced diabetologist'
        )

        self.assertEqual(doctor.user, self.user)
        self.assertEqual(doctor.license_number, 'DOC12345')
        self.assertEqual(doctor.specialization, 'diabetologist')
        self.assertEqual(doctor.years_of_experience, 10)
        self.assertEqual(doctor.consultation_fee, 250.00)
        self.assertTrue(doctor.is_accepting_patients)

    def test_license_number_must_be_unique(self):
        """Test that license_number must be unique"""
        Doctor.objects.create(
            user=self.user,
            license_number='DOC12345',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Lekarska 5',
            consultation_fee=250.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        # Create another doctor user
        user2 = User.objects.create_user(
            username='doctor2',
            password='pass',
            user_type='doctor'
        )

        # Try to create doctor with same license number
        doctor2 = Doctor(
            user=user2,
            license_number='DOC12345',  # Same license number
            specialization='endocrinologist',
            years_of_experience=5,
            office_address='ul. Inna 10',
            consultation_fee=200.00,
            working_hours_start=time(9, 0),
            working_hours_end=time(17, 0),
            education='Medical University'
        )

        with self.assertRaises(IntegrityError):
            doctor2.save()

    def test_one_to_one_relationship_with_user(self):
        """Test that Doctor has OneToOne relationship with User"""
        doctor = Doctor.objects.create(
            user=self.user,
            license_number='DOC12345',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Lekarska 5',
            consultation_fee=250.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        # Access doctor from user
        self.assertEqual(self.user.doctor_profile, doctor)

        # Access user from doctor
        self.assertEqual(doctor.user, self.user)


class DoctorStrMethodTest(TestCase):
    """Test Doctor __str__ method"""

    def test_doctor_str_representation(self):
        """Test string representation of doctor"""
        user = User.objects.create_user(
            username='doctor',
            password='pass',
            first_name='Anna',
            last_name='Nowak'
        )
        doctor = Doctor.objects.create(
            user=user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Lekarska 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        self.assertEqual(str(doctor), 'Dr. Anna Nowak - Diabetolog')


class DoctorSpecializationTest(TestCase):
    """Test doctor specialization choices"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )

    def test_endocrinologist_specialization(self):
        """Test creating endocrinologist"""
        doctor = Doctor.objects.create(
            user=self.user,
            license_number='DOC001',
            specialization='endocrinologist',
            years_of_experience=15,
            office_address='ul. Test 1',
            consultation_fee=300.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )
        self.assertEqual(doctor.specialization, 'endocrinologist')
        self.assertEqual(doctor.get_specialization_display(), 'Endokrynolog')

    def test_diabetologist_specialization(self):
        """Test creating diabetologist"""
        doctor = Doctor.objects.create(
            user=self.user,
            license_number='DOC002',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=250.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )
        self.assertEqual(doctor.specialization, 'diabetologist')
        self.assertEqual(doctor.get_specialization_display(), 'Diabetolog')

    def test_internal_medicine_specialization(self):
        """Test creating internist"""
        doctor = Doctor.objects.create(
            user=self.user,
            license_number='DOC003',
            specialization='internal_medicine',
            years_of_experience=8,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )
        self.assertEqual(doctor.specialization, 'internal_medicine')
        self.assertEqual(doctor.get_specialization_display(), 'Internista')

    def test_family_medicine_specialization(self):
        """Test creating family doctor"""
        doctor = Doctor.objects.create(
            user=self.user,
            license_number='DOC004',
            specialization='family_medicine',
            years_of_experience=5,
            office_address='ul. Test 1',
            consultation_fee=150.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )
        self.assertEqual(doctor.specialization, 'family_medicine')
        self.assertEqual(doctor.get_specialization_display(), 'Lekarz rodzinny')


class DoctorWorkingHoursTest(TestCase):
    """Test doctor working hours and days"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )

    def test_working_hours(self):
        """Test setting working hours"""
        doctor = Doctor.objects.create(
            user=self.user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(9, 0),
            working_hours_end=time(17, 30),
            education='Medical University'
        )

        self.assertEqual(doctor.working_hours_start, time(9, 0))
        self.assertEqual(doctor.working_hours_end, time(17, 30))

    def test_working_days_mon_fri(self):
        """Test Monday-Friday working days"""
        doctor = Doctor.objects.create(
            user=self.user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            working_days='mon-fri',
            education='Medical University'
        )

        self.assertEqual(doctor.working_days, 'mon-fri')
        self.assertEqual(doctor.get_working_days_display(), 'Poniedziałek-Piątek')

    def test_working_days_mon_sat(self):
        """Test Monday-Saturday working days"""
        doctor = Doctor.objects.create(
            user=self.user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            working_days='mon-sat',
            education='Medical University'
        )

        self.assertEqual(doctor.working_days, 'mon-sat')
        self.assertEqual(doctor.get_working_days_display(), 'Poniedziałek-Sobota')

    def test_default_working_days(self):
        """Test default working days is mon-fri"""
        doctor = Doctor.objects.create(
            user=self.user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        self.assertEqual(doctor.working_days, 'mon-fri')


class DoctorAcceptingPatientsTest(TestCase):
    """Test is_accepting_patients flag"""

    def test_is_accepting_patients_default_true(self):
        """Test that is_accepting_patients defaults to True"""
        user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )
        doctor = Doctor.objects.create(
            user=user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        self.assertTrue(doctor.is_accepting_patients)

    def test_set_not_accepting_patients(self):
        """Test setting is_accepting_patients to False"""
        user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )
        doctor = Doctor.objects.create(
            user=user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University',
            is_accepting_patients=False
        )

        self.assertFalse(doctor.is_accepting_patients)


class DoctorOptionalFieldsTest(TestCase):
    """Test optional fields (certifications, bio)"""

    def test_certifications_optional(self):
        """Test that certifications field is optional"""
        user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )
        doctor = Doctor.objects.create(
            user=user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
            # No certifications provided
        )

        self.assertEqual(doctor.certifications, '')

    def test_bio_optional(self):
        """Test that bio field is optional"""
        user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )
        doctor = Doctor.objects.create(
            user=user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
            # No bio provided
        )

        self.assertEqual(doctor.bio, '')

    def test_certifications_and_bio_can_be_set(self):
        """Test setting certifications and bio"""
        user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )
        doctor = Doctor.objects.create(
            user=user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University',
            certifications='Board Certified in Endocrinology',
            bio='Passionate about helping patients manage diabetes'
        )

        self.assertEqual(doctor.certifications, 'Board Certified in Endocrinology')
        self.assertEqual(doctor.bio, 'Passionate about helping patients manage diabetes')


class DoctorTimestampsTest(TestCase):
    """Test created_at and updated_at timestamps"""

    def test_created_at_set_automatically(self):
        """Test that created_at is set automatically"""
        user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )
        doctor = Doctor.objects.create(
            user=user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        self.assertIsNotNone(doctor.created_at)

    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when model is saved"""
        user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )
        doctor = Doctor.objects.create(
            user=user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=200.00,
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        original_updated_at = doctor.updated_at

        # Modify and save
        doctor.bio = 'Updated bio'
        doctor.save()

        doctor.refresh_from_db()

        self.assertGreaterEqual(doctor.updated_at, original_updated_at)


class DoctorConsultationFeeTest(TestCase):
    """Test consultation_fee field"""

    def test_consultation_fee_decimal(self):
        """Test that consultation_fee is stored as decimal"""
        from decimal import Decimal

        user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )
        doctor = Doctor.objects.create(
            user=user,
            license_number='DOC123',
            specialization='diabetologist',
            years_of_experience=10,
            office_address='ul. Test 1',
            consultation_fee=Decimal('299.99'),
            working_hours_start=time(8, 0),
            working_hours_end=time(16, 0),
            education='Medical University'
        )

        self.assertEqual(doctor.consultation_fee, Decimal('299.99'))

    def test_various_consultation_fees(self):
        """Test various consultation fee values"""
        user = User.objects.create_user(
            username='doctor',
            password='pass',
            user_type='doctor'
        )

        # Test different fee levels
        fees = [150.00, 200.50, 350.00, 500.00]

        for i, fee in enumerate(fees):
            doc_user = User.objects.create_user(
                username=f'doctor{i}',
                password='pass',
                user_type='doctor'
            )
            doctor = Doctor.objects.create(
                user=doc_user,
                license_number=f'DOC{i}',
                specialization='diabetologist',
                years_of_experience=10,
                office_address='ul. Test 1',
                consultation_fee=fee,
                working_hours_start=time(8, 0),
                working_hours_end=time(16, 0),
                education='Medical University'
            )

            from decimal import Decimal
            self.assertEqual(doctor.consultation_fee, Decimal(str(fee)))
