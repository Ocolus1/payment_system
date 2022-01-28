from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Student
import datetime
import requests
from requests.structures import CaseInsensitiveDict
import json


def defaultconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

# Create your views here.
def index(request):
    exist = "pending"
    if request.method == "POST":
        matric  = request.POST["matric_no"]
        try:
            user = Student.objects.get(matric_no=matric)
            mat_no = user.matric_no
            return redirect("details", mat_no=mat_no)
        except Student.DoesNotExist as e:
            exist = "absent"
    context = { "exist" : exist }
    return render(request, 'pay/index.html', context)

def details(request, mat_no):
    user = Student.objects.get(matric_no=mat_no)
    email = user.email
    name = user.name
    level = user.level
    amount = user.amount
    # if request.method == "POST":
        # data = {
        #     "tx_ref" : datetime.datetime.now(),
        #     "amount": amount,
        #     "currency": "NGN",
        #     "payment_options" : "card",
        #     "redirect_url" : "http://localhost:8000/process",
        #     "customer" : {
        #         "email" : email,
        #         "name" : name,
        #         "level" : level
        #     },
        #     "meta" : {
        #         "price" : amount
        #     },
        #     "customizations" : {
        #         "title" : "Payment for IESA dues",
        #         "description" : "Industrial Engineering Student Association dues"
        #     }
        # }
        # url = "https://api.flutterwave.com/v3/payments"
        # token = "FLWSECK_TEST-f3bea5571c9e44902cf2682c621e3d89-X"
        # headers = CaseInsensitiveDict()
        # body = json.dumps(data, default = defaultconverter)
        # headers["Accept"] = "application/json"
        # headers["Content-Type"] = "application/json"
        # headers["Authorization"] = f"Bearer {token}"
        # req = requests.post(url, json=body, headers=headers)
        # print(req)
        # return HttpResponse(req)
    context = { "user" : user }
    return render(request, 'pay/details.html', context)


def process(request):
    context = {  }
    return render(request, 'pay/process.html', context)