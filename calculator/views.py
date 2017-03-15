from django.shortcuts import render
from django.http import HttpResponse
from forms import CalculatorForm
from simulation import run_simulation

def index(request):
    form = CalculatorForm()
    if request.method == 'POST':
        submitted = True
        form = CalculatorForm(request.POST)
        print "posted"
        print form.__dict__
        if form.is_valid():
            run_simulation(form)
    else:
        submitted = False
    return render(request, 'calculator.html', {
        'form': form,
        'submitted': submitted
    })