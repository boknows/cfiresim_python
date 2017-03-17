from datetime import timedelta
from django.db import models


class DataPointManager(models.Manager):
    def create_from_prospect(self, prospect, billing_pool, start_date=None):
        if start_date is None:
            start_date = timezone.localtime(timezone.now()).date()
        return Discount.objects.create(
            billing_pool=billing_pool,
            code=prospect.code,
            bps_reduction=prospect.bps_reduction,
            start_date=start_date,
            extend_by=prospect.length_in_days,
            flat_rate_override=prospect.flat_rate_override,
            fully_funded_by_date=prospect.fully_funded_by_date
        )


class DataPointQuerySet(models.QuerySet):
    def yearly(self):
        return self.filter(data_date__month=1).order_by('data_date')

    def monthly(self):
        return self.all().order_by('data_date')

class DataPoint(models.Model):
    class Meta:
        app_label = 'market_data'

    objects = DataPointManager.from_queryset(DataPointQuerySet)()

    data_date = models.DateField(null=True, blank=True)
    s_and_p_composite = models.CharField(max_length=64, null=True, blank=True)
    yearly_equities_growth = models.CharField(max_length=64, null=True, blank=True)
    monthly_equities_growth = models.CharField(max_length=64, null=True, blank=True)
    dividend = models.CharField(max_length=64, null=True, blank=True)
    earnings = models.CharField(max_length=64, null=True, blank=True)
    cpi = models.CharField(max_length=64, null=True, blank=True)
    long_interest_rate = models.CharField(max_length=64, null=True, blank=True)
    real_price = models.CharField(max_length=64, null=True, blank=True)
    real_dividend = models.CharField(max_length=64, null=True, blank=True)
    real_earnings = models.CharField(max_length=64, null=True, blank=True)
    cape = models.CharField(max_length=64, null=True, blank=True)