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
        first_year_of_data = market_data.first().data_date.year
        last_year_of_data = market_data.last().data_date.year
        number_of_cycles = last_year_of_data - first_year_of_data - cycle_length

        previous_data_points = []
        for m in market_data:
            if len(previous_data_points) < cycle_length - 1:
                previous_data_points.append(m)
                continue
            simulation_cycles.append(Cycle(previous_data_points[0], m))
            if len(previous_data_points) == cycle_length - 1:
                previous_data_points.pop(0)
            previous_data_points.append(m)

        print simulation_cycles

    print cycle_length, len(market_data)

