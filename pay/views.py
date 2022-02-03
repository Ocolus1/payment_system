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
import pdfkit
import pandas as pd

config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
PAYMENT_REDIRECT_URL = settings.PAYMENT_REDIRECT_URL
PAYMENT_ENDPOINT = settings.PAYMENT_ENDPOINT
SECRET_TOKEN = settings.SECRET_TOKEN
VERIFICATION_ENDPOINT = settings.VERIFICATION_ENDPOINT
CONVERT_TO_PDF = settings.CONVERT_TO_PDF

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
            if user.paid == True :
                exist = "paid"
                context = { "exist" : exist }
                return render(request, 'pay/index.html', context)
            else:
                return redirect("details", mat_no=mat_no)
        except Student.DoesNotExist as e:
            exist = "absent"
    context = { "exist" : exist }
    return render(request, 'pay/index.html', context)


def details(request, mat_no):
    csrf_token = get_token(request)
    user = Student.objects.get(matric_no=mat_no)
    matric = user.matric_no
    email = user.email
    name = user.name
    level = user.level
    amt = user.amount
    tax = (0.05 * amt) + 100
    amount = amt + tax
    if request.method == "POST":
        data = {
            "tx_ref" : datetime.datetime.now(),
            "amount": amount,
            "currency": "NGN",
            "payment_options" : "card",
            "redirect_url" : PAYMENT_REDIRECT_URL,
            "customer" : {
                "matric" : matric,
                "email" : email,
                "name" : name,
                "level" : level
            },
            "meta" : {
                "price" : amount,
                "matric" : matric,
            },
            "customizations" : {
                "title" : "Payment for IESA dues",
                "description" : "Industrial Engineering Student Association dues"
            }
        }
        url = PAYMENT_ENDPOINT
        token = SECRET_TOKEN
        headers = CaseInsensitiveDict()
        body = json.dumps(data, default = defaultconverter)
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = f"Bearer {token}"
        req = requests.post(url, data=body, headers=headers)
        result = req.json()
        if result['status'] == "success":
            link = result['data']['link']
            return redirect(to=link)
        else:
            return HttpResponse("We cannot process your account")
    context = { "user" : user, "csrftoken": csrf_token }
    return render(request, 'pay/details.html', context)


def process(request):
    status  = request.GET.get("status")
    if status:
        if status == "cancelled" :
            return redirect(index)
        elif status == "successful" :
            tx_id = request.GET["transaction_id"]
            url = f"{VERIFICATION_ENDPOINT}{tx_id}/verify"
            token = SECRET_TOKEN
            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            headers["Authorization"] = f"Bearer {token}"
            req = requests.get(url,  headers=headers)
            result = req.json()
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
                    
                    receipt(request, matric, amount_paid)
                    options = {
                        'page-size': 'A4',
                        'orientation': 'Portrait',
                        'margin-top': '0.75in',
                        'margin-right': '0.75in',
                        'margin-bottom': '0.75in',
                        'margin-left': '0.75in',
                        'encoding': "UTF-8",
                        'custom-header': [
                            ('Accept-Encoding', 'gzip')
                        ],
                        'no-outline': None
                    }
                    pdfkit.from_url(f'{CONVERT_TO_PDF}{matric}/{amount_paid}', 
                    f'receipt/{matric}.pdf', configuration=config, options=options)
                    sendEmailWithAttach(user.email, user.dept, f'receipt/{matric}.pdf', matric)
                    context = {"header":header, 'text':text }
                    return render(request, 'pay/process.html', context)
                else:
                    header = "Fraudulent Transaction Detected"
                    text = "Repeat your payment."
                    context = {"header":header, 'text':text }
                    return render(request, 'pay/process.html', context)
            else:
                header = "Cannot Process Your Payment"
                text = "Contact your department."
                context = {"header":header, 'text':text }
                return render(request, 'pay/process.html', context)
        else:
            header = "Cannot Process Your Payment"
            text = "Contact your department."
            context = {"header":header, 'text':text }
            return render(request, 'pay/process.html', context)
    
    header = "Wrong Page"
    text = "Go back to the homepage."
    context = {"header":header, 'text':text }
    return render(request, 'pay/process.html', context)


def receipt(request, user, amount):
    user = Student.objects.get(matric_no=user)
    dept = Department.objects.get(short_name=user.dept)
    context = { "user" : user, "dept": dept, "amount": amount }
    return render(request, 'pay/receipt.html', context)
    