from django.shortcuts import render
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from models import *

def redirect(dest):
    return HttpResponseRedirect(dest)

def check_url_exists(url):
    """
    Check if a URL exists by HEAD request
    """
    r = requests.head(url, allow_redirects=True)
    if r.status_code == requests.codes.ok:
        return r.url
    else:
        return None
    return None

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, world!"})

@api_view(['GET'])
def example_route(request, arg1, arg2):
    """
    This text description for this API call
    arg1 -- A first argument
    arg2 -- A second argument
    """
        
    # Quick hack to get a Location redirect
    redirect_response = redirect('http://example.org/%s/%s/' % (arg1, arg2))
    headers = {}
    headers['Location'] = redirect_response.url
    return Response(
        status=status.HTTP_302_FOUND,
        headers=headers)


@api_view(['GET'])
def pdf(request, doi, type = None):
    """
    Get PDF file locations in JSON format.
    """
    
    pdf_types = ['figures','article']
    
    if type:
        types = []
        types.append(type)
    else:
        types = pdf_types

    data = []
    notes = []
    for pdf_type in types:
        try:
            pdf = PdfFile(doi, pdf_type)
            
            # Check if URL exists
            if check_url_exists(pdf.get_url()) is not None:
                # Add data
                item = {}
                item['url'] = pdf.get_url()
                item['size'] = pdf.get_size_from_s3()
                item['type'] = pdf_type
                data.append(item)
            else:
                # Append notes
                #notes.append('%s does not exist' % pdf.get_url())
                pass
               
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    response_list = {}
    response_list['data'] = data
        
    # Add metadata
    if len(notes) > 0:
        response_list['notes'] = notes
    response_list['results'] = len(data)

    return Response(response_list)

@api_view(['GET'])
def pdf_by_type(request, doi, type):
    """
    Get a PDF file URI
    The pdf_type can be 'figures' or 'article'
    """
    return pdf(request, doi, type)
    