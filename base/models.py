from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models.fields.json import JSONField
from django.contrib.auth.models import User
# Create your models here.

image_storage = FileSystemStorage(
    # Physical file location ROOT
    location=u'{0}/companies/'.format(settings.MEDIA_ROOT),
    # Url for file
    base_url=u'{0}companies/'.format(settings.MEDIA_URL),
)

def image_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/companies/<filename>
    return u'{0}'.format(filename)

class Company(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=500,blank=True)
    logo = models.ImageField(blank = True,upload_to=image_directory_path, storage=image_storage)
    is_dream = models.BooleanField(blank = False)
    starting_salary = models.IntegerField(blank=False)
    DAY_CHOICES = (
        ('Day 0', 'Day 0',),
        ('Day 1', 'Day 1',),
        ('Day 2', 'Day 2',),
    )
    day = models.CharField(max_length=25,choices=DAY_CHOICES,blank=False,default=DAY_CHOICES[0][0],null=False)
    
    class Meta:
        verbose_name_plural = "Company"

class Student(models.Model):
    description = models.TextField(max_length=500,blank=False)
    roll_number = models.CharField(max_length=16,blank=False,unique=True)
    contact_number = models.CharField(max_length=10,blank=False)
    college_email_id = models.EmailField(blank=False)
    GENDER_CHOICES = (
        ('F', 'Female',),
        ('M', 'Male',),
        ('O', 'Other',),
    )
    BOARD_10_CHOICES = (
        ('ICSE', 'ICSE',),
        ('SSC', 'SSC',),
        ('IGCSE', 'IGCSE',),
        ('CBSE', 'CBSE',),
        ('IB', 'IB',),
    )
    BOARD_12_CHOICES = (
        ('HSC', 'HSC',),
        ('ISC', 'ISC',),
        ('CBSE', 'CBSE',),
        ('IB', 'IB',),
        ('IGCSE', 'IGCSE',),
        ('Diploma', 'Diploma',),
    )
    STREAM_CHOICES = (
        ('BE', 'Bachelor of Engineering',),
    )
    SPECIALIZATION_CHOICES = (
         ('Comps', 'Computer Engineering',),
         ('IT', 'Information Technology',),
         ('Biomed', 'Biomedical Engineering',),
         ('EXTC', 'Electronics and Telecommunication',),
         ('Chemical', 'Chemical Engineering',),
         ('AI/DS', 'Artificial Intelligence and Data Science',),
         ('O', 'Other',),
    )
    gender = models.CharField(max_length=1,choices=GENDER_CHOICES,blank=False)
    hometown = models.CharField(max_length=25,blank=False)
    class10_board = models.CharField(max_length=10,choices=BOARD_10_CHOICES,blank=False)
    class10_school = models.CharField(max_length=50,blank=False)
    class10_percentage = models.DecimalField(max_digits=5, decimal_places=2,blank=False)
    class12_board = models.CharField(max_length=10,choices=BOARD_12_CHOICES,blank=False)
    class12_college = models.CharField(max_length=50,blank=False)
    class12_percentage = models.DecimalField(max_digits=5, decimal_places=2,blank=False)
    undergraduate_stream = models.CharField(max_length=50,choices=STREAM_CHOICES,blank=False)
    undergraduate_specialization = models.CharField(max_length=50,choices=SPECIALIZATION_CHOICES,blank=False)
    sem1_sgpi = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    sem2_sgpi = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    sem3_sgpi = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    sem4_sgpi = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    sem5_sgpi = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    sem6_sgpi = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    sem7_sgpi = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    sem8_sgpi = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    live_kt = models.BooleanField()
    year_drop = models.BooleanField()
    education_gap = models.BooleanField()
    year_joined = models.PositiveSmallIntegerField()
    expected_grad_year = models.PositiveSmallIntegerField()
    resume = models.FileField()
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    class Meta:
        verbose_name_plural = "Student"


class PlacementApplication(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL,null=True,related_name='company')
    placement_year = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(editable=False,auto_now_add=True)
    form_fields = models.TextField()

    class Meta:
        verbose_name_plural = "Placement Application"


class PlacementApplicationResponse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL,null=True,related_name='student')
    placement_application = models.ForeignKey(PlacementApplication, on_delete=models.CASCADE,related_name='placement_application')
    responded_at = models.DateTimeField(editable=False,auto_now=True)
    responses = models.TextField()

    class Meta:
        verbose_name_plural = "Placement Application Response"


class PlacementApplicationResponseFiles(models.Model):
    response = models.ForeignKey(PlacementApplicationResponse, on_delete=models.CASCADE,related_name='placement_application_response')
    label = models.CharField(max_length=50,blank=False,null=False)
    file_uploaded = models.FileField()

    class Meta:
        verbose_name_plural = "Placement Application Response Files"


class PlacementStatus(models.Model):
    student = models.OneToOneField(Student,on_delete=models.CASCADE,primary_key=True)
    offers = models.TextField()
    day0_selected_company_name = models.CharField(max_length=50,blank=True,null=True)
    day0_selected_company_salary = models.IntegerField(blank=True,null=True)
    day1_selected_company_name = models.CharField(max_length=50,blank=True,null=True)
    day1_selected_company_salary = models.IntegerField(blank=True,null=True)
    day2_selected_company_name = models.CharField(max_length=50,blank=True,null=True)
    day2_selected_company_salary = models.IntegerField(blank=True,null=True)
    placed_company_name = models.CharField(max_length=50,blank=True,null=True)
    placed_company_salary = models.IntegerField(blank=True,null=True)
    placed_company_day = models.CharField(max_length=50,blank=True,null=True)
    placed_year = models.PositiveSmallIntegerField(blank=True,null=True)
    
    class Meta:
        verbose_name_plural = "Placement Status"


