from django.shortcuts import render

from django.http import HttpResponse

from word2vec.training.demo_domain import domain_decision_for_list
from word2vec.training.demo_domain import domain_decision_detail

def show_result(request):
    
    keys = request.GET['key']
    key_list = keys.split(",") 
    
    for s in key_list:
        print(s)
    result = domain_decision_for_list(key_list)
    print(result)
    return HttpResponse(str(result))


def show_detail(request):
    keys = request.GET['key']
    key_list = keys.split(",")
    result = domain_decision_detail(key_list)
    return HttpResponse(str(result))