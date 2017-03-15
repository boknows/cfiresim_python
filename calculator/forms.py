from django import forms

class CalculatorForm(forms.Form):
    retirement_year = forms.IntegerField(initial="2017")
    retirement_end_year = forms.IntegerField(initial="2046")
    DATA_METHOD_CHOICES = (
        ('historical_all', 'Historical Data - All'),
        ('historical_specific', 'Historical Data - Specific Years'),
        ('constant_market_growth', 'Constant Market Growth'),
        ('single_simulation', 'Single Simulation Cycle'),
    )
    data_method = forms.ChoiceField(choices=DATA_METHOD_CHOICES)
    portfolio_value = forms.IntegerField(initial="1000000")
    equities = forms.IntegerField(initial="75")
    bonds = forms.IntegerField(initial="25")
    gold = forms.IntegerField(initial="0")
    cash = forms.IntegerField(initial="0")
    fees = forms.DecimalField(initial="0.18")
    growth_of_cash = forms.DecimalField(initial="0.25")
    SPENDING_PLAN_CHOICES = (
        ('inflation_adjusted', 'Inflation Adjusted'),
    )
    spending_plan = forms.ChoiceField(choices=SPENDING_PLAN_CHOICES)
    initial_yearly_spending = forms.IntegerField(initial="40000")
    ss_annual_value = forms.IntegerField(initial="0")
    ss_start_year = forms.IntegerField(initial="2032")
    ss_end_year = forms.IntegerField(initial="2100")
    ss_spouse_annual_value = forms.IntegerField(initial="0")
    ss_spouse_start_year = forms.IntegerField(initial="2032")
    ss_spouse_end_year = forms.IntegerField(initial="2100")