from django.http import HttpResponse


# Create your views here.
def index(request):
    return HttpResponse("Here's the text of the Web page.")