from market_data.models import DataPoint

class Cycle:
    def __init__(self, start, end):
        self.range_start = start.data_date
        self.range_end = end.data_date

    @property
    def start_CPI(self):
        start_CPI_lookup = DataPoint.objects.get(data_date=self.range_start)
        return start_CPI_lookup.cpi


def run_simulation(form):
    market_data = DataPoint.objects.all().yearly()

    simulation_cycles = []
    if form.is_valid:
        cycle_length = form.cleaned_data['retirement_end_year'] - form.cleaned_data['retirement_year'] + 1

    print cycle_length, len(market_data)
    
