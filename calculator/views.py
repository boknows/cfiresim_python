from pprint import pprint

from django.shortcuts import render
from django.http import HttpResponse
from forms import CalculatorForm
from simulation import run_simulation

def index(request):
    form = CalculatorForm()
    output = None
    if request.method == 'POST':
        submitted = True
        form = CalculatorForm(request.POST)
        print "posted"
        print form.__dict__
        if form.is_valid():
            all_output = []
            simulation = run_simulation(form)


    else:
        submitted = False
    return render(request, 'calculator.html', {
        'output': output,
        'form': form,
        'submitted': submitted
    })
