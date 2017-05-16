from pprint import pprint
from dateutil.relativedelta import relativedelta
from decimal import Decimal as D
from market_data.models import DataPoint
from datetime import datetime
import math


class Input:
    def __init__(self, form):
        self.retirement_year = form.cleaned_data['retirement_year']
        self.retirement_end_year = form.cleaned_data['retirement_end_year']
        self.data_method = form.cleaned_data['data_method']
        self.portfolio_value = form.cleaned_data['portfolio_value']
        self.equities = form.cleaned_data['equities']
        self.bonds = form.cleaned_data['bonds']
        self.gold = form.cleaned_data['gold']
        self.cash = form.cleaned_data['cash']
        self.fees = form.cleaned_data['fees']
        self.growth_of_cash = form.cleaned_data['growth_of_cash']
        self.spending_plan = form.cleaned_data['spending_plan']
        self.initial_yearly_spending = form.cleaned_data['initial_yearly_spending']
        self.ss_annual_value = form.cleaned_data['ss_annual_value']
        self.ss_start_year = form.cleaned_data['ss_start_year']
        self.ss_end_year = form.cleaned_data['ss_end_year']
        self.ss_spouse_annual_value = form.cleaned_data['ss_spouse_annual_value']
        self.ss_spouse_start_year = form.cleaned_data['ss_spouse_start_year']
        self.ss_spouse_end_year = form.cleaned_data['ss_spouse_end_year']


class Cycle:
    def __init__(self, data_points):
        self.range_start = data_points[0].date
        self.range_end = data_points[-1].date
        self.start_CPI = data_points[0].cpi
        self.years = relativedelta(self.range_end, self.range_start).years + 1
        self.sim = []

        for i in range (0, self.years):
            data_point = data_points[i]
            self.sim.append(Segment(
                date=self.range_start + relativedelta(years=i),
                start_CPI=self.start_CPI,
                yearly_equities_growth=data_point.yearly_equities_growth,
                cpi=data_point.cpi,
                dividend=data_point.dividend,
                s_and_p_composite=data_point.s_and_p_composite,
                long_interest_rate=data_point.long_interest_rate
            ))


class Segment:
    def __init__(self, date, start_CPI, yearly_equities_growth, cpi, dividend, s_and_p_composite, long_interest_rate):
        self.start_CPI = D(start_CPI)
        self.date = date
        self.portfolio = {
            "start": None,
            "end": None,
            "inflation_adjusted_start": None,
            "inflation_adjusted_end": None,
            "fees": None
        }
        self.spending = None
        self.inflation_adjusted_spending = None
        self.equities = {
            "start": None,
            "growth": None,
            "val": None
        }
        self.bonds = {
            "start": None,
            "growth": None,
            "val": None
        }
        self.gold = {
            "start": None,
            "growth": None,
            "val": None
        }
        self.cash = {
            "start": None,
            "growth": None,
            "val": None
        }
        self.dividends = {
            "growth": None,
            "val": None
        }
        self.fees = None

        self.yearly_equities_growth = D(yearly_equities_growth)
        self.cumulative_inflation = 1 + (D(cpi) - self.start_CPI) / self.start_CPI
        self.sum_of_adjustments = None
        self.cpi = cpi
        self.dividend = dividend
        self.s_and_p_composite = s_and_p_composite
        self.long_interest_rate = long_interest_rate

class Data():
    def __init__(self,
                 date,
                 cpi,
                 yearly_equities_growth,
                 s_and_p_composite,
                 long_interest_rate,
                 dividend,
                 ):
        self.date = date
        self.cpi = cpi
        self.yearly_equities_growth = yearly_equities_growth
        self.s_and_p_composite = s_and_p_composite
        self.long_interest_rate = long_interest_rate
        self.dividend = dividend


def run_simulation(form):
    market_data_lookup = list(DataPoint.objects.all().yearly())
    market_data = []
    for m in market_data_lookup:
        market_data.append(
            Data(
                date=m.data_date,
                cpi=m.cpi,
                yearly_equities_growth=m.yearly_equities_growth,
                s_and_p_composite=m.s_and_p_composite,
                long_interest_rate=m.long_interest_rate,
                dividend=m.dividend
            )
        )
    simulation_cycles = []
    inputs = Input(form)
    if form.is_valid:
        cycle_length = inputs.retirement_end_year - inputs.retirement_year + 1
        first_year_of_data = market_data[0].date.year
        last_year_of_data = market_data[-1].date.year
        number_of_cycles = last_year_of_data - first_year_of_data - cycle_length

        previous_data_points = []
        for m in market_data:
            if len(previous_data_points) < cycle_length:
                previous_data_points.append(m)
                continue
            simulation_cycles.append(Cycle(previous_data_points))
            if len(previous_data_points) == cycle_length:
                previous_data_points.pop(0)
            previous_data_points.append(m)

        for cycle in simulation_cycles:
            for i in range(0, len(cycle.sim)):
                calculate_adjustments(inputs=inputs, segment=cycle.sim[i], segment_num=i)
                calculate_starting_portfolio(inputs=inputs,
                                             cycle=cycle,
                                             segment_num=i
                                             )
                calculate_market_gains(inputs=inputs, cycle=cycle, segment_num=i)
                calculate_ending_portfolio(inputs=inputs, segment=cycle.sim[i])

        chart_data = []
        spending_data = []
        interval = len(simulation_cycles)
        cycle_length = len(simulation_cycles[0].sim)
        sim_length = interval + cycle_length - 1

        for i in range(0, interval):
            chart_data.append([])
            spending_data.append([])
            for j in range(0, sim_length):
                chart_data[i].append("null")
                spending_data[i].append("null")

        first_year = simulation_cycles[0].sim[0].date
        for i in range(0, len(simulation_cycles)):
            for j in range(0, cycle_length):
                index = relativedelta(simulation_cycles[i].sim[j].date, first_year).years
                chart_data[i][index] = int(simulation_cycles[i].sim[j].portfolio['inflation_adjusted_end'])


        return chart_data


def calculate_starting_portfolio(inputs, cycle, segment_num):
    first_segment = True if segment_num == 0 else False
    segment = cycle.sim[segment_num]
    spending = calculate_spending(inputs, segment, first_segment)
    if cycle.sim[segment_num].date == cycle.range_start:
        cycle.sim[segment_num].portfolio['start'] = inputs.portfolio_value - \
                                                    inputs.initial_yearly_spending + segment.sum_of_adjustments
    else:
        cycle.sim[segment_num].portfolio['start'] = cycle.sim[segment_num-1].portfolio['end'] - \
                                                    spending + segment.sum_of_adjustments

def calculate_ending_portfolio(inputs, segment):
    fees_incurred = (segment.portfolio['start'] +
                     segment.equities['growth'] +
                     segment.bonds['growth'] +
                     segment.cash['growth'] +
                     segment.gold['growth']
                     ) * (inputs.fees / 100)
    segment.fees = fees_incurred

    # Calculate current allocation percentages after all market gains are taken into consideration
    totalEnd = segment.equities['end'] + segment.bonds['end'] + segment.cash['end'] + segment.gold['end']
    current_percent_equities = segment.equities['end'] / totalEnd
    current_percent_cash = segment.cash['end'] / totalEnd
    current_percent_bonds = segment.bonds['end'] / totalEnd
    current_percent_gold = segment.gold['end'] / totalEnd

    #Equally distribute fees and portfolio adjustments amongst portfolio based on allocation percentages
    segment.equities['end'] = segment.equities['end'] - (current_percent_equities * fees_incurred)
    segment.cash['end'] = segment.cash['end'] - (current_percent_cash * fees_incurred)
    segment.bonds['end'] = segment.bonds['end'] - (current_percent_bonds * fees_incurred)
    segment.gold['end'] = segment.gold['end'] - (current_percent_gold * fees_incurred)

    #Sum all assets to determine portfolio end value.
    totalEnd = segment.equities['end'] + segment.bonds['end'] + segment.cash['end'] + segment.gold['end']
    segment.portfolio['end'] = totalEnd if totalEnd > 0 else 0
    segment.portfolio['inflation_adjusted_end'] = segment.portfolio['end'] / segment.cumulative_inflation


def calculate_spending(inputs, segment, first_segment):
    if first_segment:
        spending = inputs.initial_yearly_spending
    else:
        spending = inputs.initial_yearly_spending * segment.cumulative_inflation

    segment.spending = round(D(spending),2)
    segment.inflation_adjusted_spending = round(D(spending / segment.cumulative_inflation),2)
    return spending

def calculate_market_gains(inputs, cycle, segment_num):
    segment = cycle.sim[segment_num]
    portfolio = segment.portfolio['start']

    allocation = calculate_allocation(inputs)

    #Equities
    segment.equities['start'] = (allocation['equities'] * portfolio)
    segment.equities['growth'] = (segment.equities['start'] * segment.yearly_equities_growth)
    #Dividends
    segment.dividends['growth'] = segment.equities['start'] * \
                                  D(segment.dividend)/D(segment.s_and_p_composite)
    segment.equities['end'] = segment.equities['start'] + segment.equities['growth'] + segment.dividends['growth']
    #Bonds
    segment.bonds['start'] = (allocation['bonds'] * portfolio)
    bonds_this_year = D(segment.long_interest_rate) / 100
    if len(cycle.sim)-1 == segment_num:
        segment.bonds['growth'] = segment.bonds['start'] * bonds_this_year
    else:
        bonds_next_year = D(cycle.sim[segment_num+1].long_interest_rate)/100
        bonds_growth1 = bonds_this_year * ((1 - D((math.pow((1 + bonds_next_year), -9)))) / bonds_next_year)
        bonds_growth2 = (1 / D((math.pow((1 + bonds_next_year), 9))) - 1)
        segment.bonds['growth'] = segment.bonds['start'] * (bonds_growth1 + bonds_growth2 + bonds_this_year)
    segment.bonds['end'] = segment.bonds['start'] + segment.bonds['growth']
    #Gold  TODO: Fill in DB and call value heret
    segment.gold['start'] = (allocation['gold'] * portfolio)
    segment.gold['growth'] = 0
    segment.gold['end'] = segment.gold['start'] + segment.gold['growth']
    #Cash
    segment.cash['start'] = (allocation['cash'] * portfolio)
    segment.cash['growth'] = segment.cash['start'] * inputs.growth_of_cash
    segment.cash['end'] = segment.cash['start'] + segment.cash['growth']


def calculate_adjustments(inputs, segment, segment_num):
    current_year = datetime.now().year
    ss_and_pension_adjustments = 0
    sum_of_adjustments = 0

    if (segment_num >= (inputs.ss_start_year - current_year)) and (segment_num <= (inputs.ss_end_year - current_year)):
        ss_and_pension_adjustments += (inputs.ss_annual_value * segment.cumulative_inflation)

    sum_of_adjustments += ss_and_pension_adjustments
    segment.sum_of_adjustments = sum_of_adjustments


def calculate_allocation(inputs):
    return {
        "equities": D(inputs.equities) / 100,
        "bonds": D(inputs.bonds) / 100,
        "gold": D(inputs.gold) / 100,
        "cash": D(inputs.cash) / 100,
    }
