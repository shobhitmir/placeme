from django import forms
from django.forms.models import model_to_dict
from django.http import response
from django.http.response import HttpResponse
from django.shortcuts import redirect, render, HttpResponseRedirect, get_object_or_404
from django.contrib.auth import login,authenticate, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import pandas as pd
from .models import Company, PlacementApplicationResponse,Student,PlacementApplication
from django.contrib.auth.password_validation import password_changed,validate_password
from .forms import AddCompanyForm,StudentDetailsForm,CompanyApplicationForm
from django.core.exceptions import ValidationError
import json

# Create your views here.

def index_view(request):
    if request.user is not None:
        logout(request)
    return render(request,'index.html')

@csrf_exempt
def login_handle_view(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pwd')
        user = authenticate(username = username, password=password)
        if user is not None:
            login(request,user)
            return render(request,'home.html')
        else:
            messages.error(request,"Invalid username or password.")
            return redirect(request.META['HTTP_REFERER'])
    else:
        return render(request,'home.html')


def student_cred_view(request):
    if "GET" == request.method:
        return render(request, 'student_cred.html', {})
    else:
        file = request.FILES["excel_file"]
        if file.name.endswith('.csv'):
            dataset = pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            dataset = pd.read_excel(file)
        else:
            messages.error(request,"Invalid file format.")
            return render(request, 'student_cred.html', {})
        student_details = dataset.iloc[:,0].values
        pwd = []
        for student_uname in student_details:
            username = student_uname
            password = User.objects.make_random_password()
            user = User.objects.create_user(username=username,email=username,password=password)
            pwd.append(password)
        dataset['password'] = pwd
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=credentials.csv'
        dataset.to_csv(path_or_buf=response)  # with other applicable parameters
        return response


def company_view(request):
    companies = Company.objects.all()
    if not companies.exists():
        companies = None 
    if request.method == 'GET':
        addform = AddCompanyForm()
        return render(request,'company.html',{'companies': companies, 'addform':addform})
    else:
        if request.POST.get("addcompany"):
            addform = AddCompanyForm(request.POST, request.FILES)
            if addform.is_valid():
                addform.save()
            return HttpResponseRedirect(request.path_info)
        elif request.POST.get("deletecompany"):  # You can use else in here too if there is only 2 submit types.
            id = request.POST.get("deletecompany")
            instance = Company.objects.get(id=id)
            instance.delete()
            return HttpResponseRedirect(request.path_info)
        elif request.POST.get("updatecompany"): 
            id = request.POST.get("updatecompany")
            company = get_object_or_404(Company,pk=id)
            form = AddCompanyForm(request.POST, request.FILES, instance=company)
            if form.is_valid():
	            form.save()
            return HttpResponseRedirect(request.path_info)


def profile_view(request):
    if request.method == 'GET':
        return render(request,'profile.html')
    else:
        if request.POST.get("profile"):
            fn = request.POST['fn']
            ln = request.POST['ln']
            username = request.POST['username'] 
            email = request.POST['email']
            if User.objects.exclude(pk=request.user.id).filter(username=username).exists():
                messages.error(request,"Username already exists.")
                return redirect(request.META['HTTP_REFERER'])
            if User.objects.exclude(pk=request.user.id).filter(email=email).exists():
                messages.error(request,"Email already exists.")
                return redirect(request.META['HTTP_REFERER'])
            user=User.objects.get(pk=request.user.id)
            user.first_name=fn
            user.last_name=ln
            user.email=email
            user.username=username
            user.save()
        elif request.POST.get("pwd"):
            username = request.POST['username'] 
            old_pwd = request.POST['old']
            new_pwd = request.POST['new']
            confirm_pwd = request.POST['confirm']
            user=User.objects.get(pk=request.user.id)
            if not user.check_password(old_pwd):
                messages.error(request,"Old password incorrect.")
                return redirect(request.META['HTTP_REFERER'])
            if new_pwd != confirm_pwd:
                messages.error(request,"Passwords do not match.")
                return redirect(request.META['HTTP_REFERER'])
            try:
                validate_password(new_pwd,user=user)
            except ValidationError as err:
                messages.error(request,err.messages[0])
                return redirect(request.META['HTTP_REFERER'])
            user.set_password(new_pwd)
            user.save()
            user = authenticate(username = username, password=new_pwd)
            if user is not None:
                login(request,user)
        return HttpResponseRedirect(request.path_info)


def academics_view(request):
    if request.method == 'GET':
        studform = StudentDetailsForm()
        try:
            student = Student.objects.get(user_id=request.user.id)
            for field,attr in zip(studform.fields,student._meta.get_fields()[1:]):
                studform[field].initial = getattr(student,attr.name)
            return render(request,'academics.html',{'form':studform})
        except:  
            return render(request,'academics.html',{'form':studform})
    else:
        try:
            student = get_object_or_404(Student,user_id=request.user.id)
            studform = StudentDetailsForm(request.POST, request.FILES, instance=student)
            if studform.is_valid():
	            studform.save()
            return HttpResponseRedirect(request.path_info)
        except:
            studform = StudentDetailsForm(request.POST, request.FILES)
            studform.instance.user = request.user
            if studform.is_valid():
                studform.save()
            return HttpResponseRedirect(request.path_info)

def FormBuilder(params,required):
    keys = list(params.keys())
    values = list(params.values())
    form_title = params.get('title')
    form_description = params.get('description')
    formfields = {}
    for i in range(len(keys)):
        if 'type' in keys[i] :
            form_type = values[i]
            if form_type == 'Text':
                formfields[values[i-1]] = forms.CharField(max_length=25,required=required)
            elif form_type == 'Paragraph':
                formfields[values[i-1]] = forms.CharField(widget=forms.Textarea,required=required)
            elif form_type == 'Email':
                formfields[values[i-1]] = forms.EmailField(required=required)
            elif form_type == 'Integer':
                formfields[values[i-1]] = forms.IntegerField(required=required)
            elif form_type == 'Decimal':
                formfields[values[i-1]] = forms.DecimalField(max_digits=6, decimal_places=2,required=required)
            elif form_type == 'File Upload':
                formfields[values[i-1]] = forms.FileField(required=required)
            elif form_type == 'Choice':
                choices = [(choice,choice) for choice in params[keys[i+1]]]
                formfields[values[i-1]] = forms.ChoiceField(choices=choices,required=required)
    ApplicationForm = type('ApplicationForm',(CompanyApplicationForm,),formfields)
    form = ApplicationForm()
    return form,form_title,form_description
        
def todict(querydict):
    params = {}
    for key in querydict.keys():
        if len(querydict.getlist(key))>1:
            params[key] = querydict.getlist(key)
        else:
            params[key] = querydict[key]
    return params

def createform_view(request,company_id):
    if request.method == 'GET':
        return render(request,'createform.html',{'company_id':company_id})
    
    elif request.POST.get("preview"):
        placement_year = request.POST.get('year')
        params = todict(request.POST)
        form,form_title,form_description = FormBuilder(params,False)
        params = json.dumps(params,indent=2)
        return render(request,'preview.html',{'form':form,'title':form_title,'description':form_description,'params':params,'company_id':company_id,'placement_year':placement_year})

    elif request.POST.get("back"):
        return render(request,'createform.html',{'company_id':company_id})
    
    elif request.POST.get("save"):
        form_fields = request.POST.get("params")
        placement_year = request.POST.get('year')
        company = Company.objects.get(id=company_id)
        placement_application = PlacementApplication(company=company,form_fields=form_fields,placement_year=placement_year) 
        placement_application.save()
        return redirect('company')


def clean_responses(responses,fields):
    kl1 = list(fields)
    kl2 = list(responses)
    kv1 = list(fields.values())
    kv2 = list(responses.values())
    for i in range(len(kl1)):
        if i<len(kl2) and kl1[i] != kl2[i]:
            kl2.insert(i,kl1[i])
            kv2.insert(i,None)
        elif i>=len(kl2):
            kl2.append(kl1[i])
            kv2.append(None)
    responses = {}
    for i in range(len(kl2)):
        responses[kl2[i]] = kv2[i]
    return responses
    

def placement_applications_view(request):
    if request.method == 'GET':
        applications = PlacementApplication.objects.all()
        if not applications.exists():
            applications = None 
        fields = []
        for application in applications:
            form_fields = json.loads(application.form_fields)
            fields.append(form_fields)
        applications = zip(applications,fields)
        return render(request,'applications.html',{'applications':applications})

    elif  request.method == 'POST':
        if request.POST.get("delete"):
            id = request.POST.get("delete")
            instance = PlacementApplication.objects.get(id=id)
            instance.delete()
            return redirect('applications')

        if request.POST.get("preview"):
            params = request.POST.get("preview")
            params = params.replace("'",'"')
            params = json.loads(params)
            form,form_title,form_description = FormBuilder(params,False)
            return render(request,'fillform.html',{'form':form,'title':form_title,'description':form_description})

        if request.POST.get("back"):
            return redirect('applications')
        
        if request.POST.get("responses"):
            return redirect('applications')

        if request.POST.get("apply"):
            form_id = request.POST.get("id")
            placement_application = PlacementApplication.objects.get(id=form_id)
            student = Student.objects.get(user=request.user)
            params = request.POST.get("apply")
            params = params.replace("'",'"')
            params = json.loads(params)
            form,form_title,form_description = FormBuilder(params,True)
            try:
                placement_application_response = get_object_or_404(PlacementApplicationResponse,placement_application=placement_application,student=student)
                responses = json.loads(placement_application_response.responses)
                responses = clean_responses(responses,form.fields)

                form.set_initial(responses)
            except:
                responses = None
            return render(request,'fillform.html',{'form':form,'title':form_title,'description':form_description,'form_id':form_id})

        if request.POST.get("filled"):
            form_id = request.POST.get('filled')
            responses = todict(request.POST)
            files = request.FILES
            del responses['csrfmiddlewaretoken']
            del responses['filled']
            responses = json.dumps(responses)
            student = Student.objects.get(user=request.user)
            placement_application = PlacementApplication.objects.get(id=form_id)
            try:
                placement_application_response = get_object_or_404(PlacementApplicationResponse,placement_application=placement_application,student=student)
                placement_application_response.responses = responses
            except:
                placement_application_response = PlacementApplicationResponse(
                student=student,responses=responses,placement_application=placement_application) 
            placement_application_response.save()
            return redirect('applications')



        