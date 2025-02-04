import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, Sum, Min, F, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView, ListView, RedirectView

from market.models import StockInstrument, Deal, InstrumentType
from operations.models import Operation
from tinkoff_api import TinkoffProfile

logger = logging.getLogger(__name__)


class UpdateInvestmentAccountMixin:
    def get(self, *args, **kwargs):
        self.investment_account = getattr(self.request.user, 'default_investment_account', None)
        if self.investment_account:
            self.investment_account.update_portfolio()
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.investment_account:
            context['currency_assets'] = \
                self.investment_account.currency_assets.all().select_related('currency').distinct()
        return context


class IndexView(LoginRequiredMixin, RedirectView):
    pattern_name = 'operations'


class OperationsView(LoginRequiredMixin, UpdateInvestmentAccountMixin, ListView):
    template_name = 'operations.html'
    context_object_name = 'operations'
    model = Operation

    def get_queryset(self):
        figi = self.request.GET.get('figi')
        try:
            instrument_object = InstrumentType.objects.get(figi=figi)
        except ObjectDoesNotExist:
            queryset = Operation.objects.filter(
                investment_account=self.investment_account,
            ).select_related()
        else:
            queryset = Operation.objects.filter(
                investment_account=self.investment_account,
                instrument=instrument_object
            ).select_related()
        # XXX
        return (
            queryset
            .annotate(lots=F('quantity')/Coalesce(F('instrument__lot'), 1))
            .select_related('currency', 'instrument')
            .distinct().order_by('-date')
        )


class DealsView(LoginRequiredMixin, UpdateInvestmentAccountMixin, TemplateView):
    template_name = 'deals.html'

    def get_context_data(self, **kwargs):
        # TODO: все в бизнес-логику
        figi = self.request.GET.get('figi')
        try:
            figi_object = StockInstrument.objects.get(figi=figi)
        except ObjectDoesNotExist:
            queryset = Deal.objects.filter(investment_account=self.investment_account)
        else:
            queryset = Deal.objects.filter(investment_account=self.investment_account, figi=figi_object)

        context = super().get_context_data(**kwargs)
        opened_deals = list(
            queryset.opened()
            .annotate(
                earliest_operation_date=Min('operations__date'),
                instrument_name=F('instrument__name'),
                instrument_figi=F('instrument__figi'),
                abbreviation=Subquery(
                    Operation.objects.filter(deal=OuterRef('pk')).values('currency__abbreviation')[:1]
                )
            )
            .order_by('-earliest_operation_date')
            .values()
        )
        if self.investment_account:
            with TinkoffProfile(self.investment_account.token) as tp:
                portfolio = tp.portfolio()['payload']['positions']
                portfolio = {i['figi']: i for i in portfolio}
            for deal in opened_deals:
                figi_figi = deal['instrument_figi']
                asset = portfolio[figi_figi]
                price = asset['averagePositionPrice']['value'] * asset['balance']
                expected_price = price + asset['expectedYield']['value']
                if price < expected_price:
                    deal['expected_percent_profit'] = ((expected_price / price)-1)*100
                else:
                    deal['expected_percent_profit'] = -(1-(expected_price/price))*100
                deal['expected_profit'] = asset['expectedYield']['value']
                deal['lots_left'] = asset['lots']
        context['opened_deals'] = opened_deals
        context['closed_deals'] = (
            queryset.closed()
            .annotate(
                latest_operation_date=Max('operations__date'),
                earliest_operation_date=Min('operations__date'),
                abbreviation=Subquery(
                    Operation.objects.filter(deal=OuterRef('pk')).values('currency__abbreviation')[:1]
                ),
                profit=Sum('operations__payment')+Sum('operations__commission'))
            .order_by('-latest_operation_date')
        ).select_related('instrument').distinct()
        return context
