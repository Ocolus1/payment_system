from django.shortcuts import redirect, render
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.core.mail import EmailMessage
from .models import Department, Student
from django.conf import settings
import datetime
import requests
from requests.structures import CaseInsensitiveDict
import json
import pandas as pd
from weasyprint import HTML
from django.template.loader import render_to_string
import socket




PAYMENT_REDIRECT_URL = settings.PAYMENT_REDIRECT_URL
PAYMENT_ENDPOINT = settings.PAYMENT_ENDPOINT
SECRET_TOKEN = settings.SECRET_TOKEN
SECRET_TOKEN_PROD = settings.SECRET_TOKEN_PROD
VERIFICATION_ENDPOINT = settings.VERIFICATION_ENDPOINT
CONVERT_TO_PDF = settings.CONVERT_TO_PDF
TAX = settings.TAX

def defaultconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def sendEmailWithAttach(emailto, dept, file_path, matric):
    html_content = "Your payment was successful. Kindly find the attached receipt."
    sub = f"Payment receipt from {dept}"
    email = EmailMessage(sub, html_content, 'Cypherspot <do_not_reply@domain.com>', [emailto])
    email.content_subtype = "html"

    file = open(file_path, 'rb')
    email.attach(f'{matric}.pdf', file.read(), 'text/pdf')

    email.send()
    return "sent successfully"

def add_to_db(file_path):
    df = pd.read_excel(file_path)

    data = []

    for l in range(0, int(df.size / 6)):
        m = []
        for i in df.iloc[l]:
            m.append(i)
        data.append(m)

    for i in data:
        Student.objects.create(
            matric_no = i[0],
            name = i[1],
            email = i[2],
            phone = i[3],
            level = i[4],
            amount = i[5],
            dept = "IESA"
        )
    return "Added successfully"


# Create your views here.
def index(request):
    exist = "pending"
    # add_to_db('data/three.xlsx')
    if request.method == "POST":
        matric  = request.POST["matric_no"]
        try:
            user = Student.objects.get(matric_no=matric)
            mat_no = user.matric_no
            dept = user.dept
            if user.paid == True :
                exist = "paid"
                context = { "exist" : exist }
                return render(request, 'pay/index.html', context)
            else:
                return redirect("details", dept=dept, mat_no=mat_no)
        except Student.DoesNotExist as e:
            exist = "absent"
    context = { "exist" : exist }
    return render(request, 'pay/index.html', context)


def details(request, dept, mat_no):
    csrf_token = get_token(request)
    user = Student.objects.get(matric_no=mat_no)
    matric = user.matric_no
    email = user.email
    name = user.name
    level = user.level
    phone = user.phone
    amt = user.amount
    department = Department.objects.get(short_name=dept)
    tax = int(TAX)
    amount = amt + tax
    if request.method == "POST":
        data = {
            "tx_ref" : datetime.datetime.now(),
            "amount": amount,
            "currency": "NGN",
            "payment_options" : "card",
            "redirect_url" : f"{PAYMENT_REDIRECT_URL}/{dept}",
            "customer" : {
                "matric" : matric,
                "email" : email,
                "name" : name,
                "level" : level,
                "phone_number" : phone
            },
            "meta" : {
                "price" : amount,
                "matric" : matric,
            },
            "customizations" : {
                "title" : f"Payment for {dept} dues",
                "description" : f"{department.description}"
            }
        }
        url = PAYMENT_ENDPOINT
        token = SECRET_TOKEN #for development
        # token = SECRET_TOKEN_PROD #for production
        headers = CaseInsensitiveDict()
        body = json.dumps(data, default = defaultconverter)
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = f"Bearer {token}"
        req = requests.post(url, data=body, headers=headers)
        result = req.json()
        req.close()
        if result['status'] == "success":
            link = result['data']['link']
            return redirect(to=link)
        else:
            return HttpResponse("We cannot process your account")
    context = { "user" : user, "csrftoken": csrf_token, "department":department }
    return render(request, 'pay/details.html', context)


def process(request, dept):
    status  = request.GET.get("status")
    dept = Department.objects.get(short_name=dept)
    if status:
        if status == "cancelled" :
            return redirect(index)
        elif status == "successful" :
            tx_id = request.GET["transaction_id"]
            url = f"{VERIFICATION_ENDPOINT}{tx_id}/verify"
            token = SECRET_TOKEN #for development
            # token = SECRET_TOKEN_PROD #for production
            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            headers["Authorization"] = f"Bearer {token}"
            req = requests.get(url,  headers=headers)
            result = req.json()
            req.close()
            if result['status'] == "success" :
                amount_paid = result['data']['charged_amount']
                amount_to_pay = result['data']['meta']['price']
                matric  = result['data']['meta']['matric']
                reference  = result['data']['flw_ref']
                if float(amount_paid) >= float(amount_to_pay) :
                    user = Student.objects.get(matric_no=matric)
                    user.paid = True
                    user.paid_date = datetime.datetime.now()
                    user.ref = reference
                    user.save()
                    header = "Your payment was successful"
                    text = "Check your email for your receipt."

                    # HTML(f'{CONVERT_TO_PDF}{matric}/{amount_paid}').write_pdf(f'receipt/{matric}.pdf')
                    user = Student.objects.get(matric_no=matric)
                    dept = Department.objects.get(short_name=user.dept)
                    html_string = render_to_string('pay/receipt.html', { "user" : user, "dept": dept, "amount": amount_paid})
                    print("holla")
                    HTML(string=html_string).write_pdf(f'receipt/{dept.short_name}/{matric}.pdf')
                    print("super")
                    sendEmailWithAttach(user.email, user.dept, f'receipt/{dept.short_name}/{matric}.pdf', matric)
                    context = {"header":header, 'text':text, "dept": dept }
                    return render(request, 'pay/process.html', context)
                else:
                    header = "Fraudulent Transaction Detected"
                    text = "Repeat your payment."
                    context = {"header":header, 'text':text, "dept": dept }
                    return render(request, 'pay/process.html', context)
            else:
                header = "Cannot Process Your Payment"
                text = "Contact your department."
                context = {"header":header, 'text':text, "dept": dept }
                return render(request, 'pay/process.html', context)
        else:
            header = "Cannot Process Your Payment"
            text = "Contact your department."
            context = {"header":header, 'text':text, "dept": dept }
            return render(request, 'pay/process.html', context)

    header = "Wrong Page"
    text = "Go back to the homepage."
    # HTML(string=html_string, base_url="https://cypherpay.pythonanywhere.com").write_pdf('mys.pdf', presentational_hints=True)
    context = {"header":header, 'text':text, "dept": dept }
    return render(request, 'pay/process.html', context)


def receipt(request, user, amount):
    user = Student.objects.get(matric_no=user)
    dept = Department.objects.get(short_name=user.dept)
    context = { "user" : user, "dept": dept, "amount": amount }
    return render(request, 'pay/receipt.html', context)


def custom_page_not_found_view(request, exception):
    return render(request, "pay/errors/404.html", {})

def custom_error_view(request, exception=None):
    return render(request, "pay/errors/500.html", {})

def custom_permission_denied_view(request, exception=None):
    return render(request, "pay/errors/403.html", {})

def custom_bad_request_view(request, exception=None):
    return render(request, "errors/400.html", {})
