import datetime as dt
import logging
from functools import wraps
from typing import Optional
from urllib.parse import urljoin

import requests

from tinkoff_api.exceptions import PermissionDeniedError, UnauthorizedError, UnknownError, InvalidArgumentError, \
    InvalidTokenError


logger = logging.getLogger(__name__)


def only_with_production_token(func):
    """ Ограничивает доступ к функциям, для которых нужен trading_token """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if getattr(self, 'is_production_token_valid', False):
            return func(self, *args, **kwargs)
        raise PermissionDeniedError('Авторизуйтесь через production_token')
    return wrapper


def only_authorized(func):
    """ Только для авторизованных пользователей """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if getattr(self, 'is_authorized', False):
            return func(self, *args, **kwargs)
        raise UnauthorizedError('Авторизуйтесь, используя метод .auth()')
    return wrapper


def generate_url(func):
    """ Генерирует url из названия обернутой функции и типа токена """
    @wraps(func)
    def wrapper(profile, *args, **kwargs):
        if kwargs.get('url') is not None:
            raise InvalidArgumentError('Нельзя передавать аргумент url')
        path = func.__name__.split('_')
        if profile.is_sandbox_token_valid:
            path.insert(0, 'sandbox')
        else:
            path.insert(0, 'production')
        url = TinkoffApiUrl.url(*path)
        kwargs['url'] = url
        result = func(profile, *args, **kwargs)
        return result
    return wrapper


class TinkoffApiUrl:
    production_url = 'https://api-invest.tinkoff.ru/openapi/'
    production_streaming_url = 'wss://api-invest.tinkoff.ru/openapi/md/v1/md-openapi/ws'
    sandbox_url = 'https://api-invest.tinkoff.ru/openapi/sandbox/'

    class _Url:
        def __init__(self, url):
            self._url = url

        def __getattr__(self, attr):
            attr = attr.strip('/') + '/'
            return TinkoffApiUrl._Url(urljoin(self._url, attr))

        def url(self):
            return self._url

    production = _Url(production_url)
    prod = production
    sandbox = _Url(sandbox_url)
    sand = sandbox

    @staticmethod
    def url(*args):
        if not args:
            raise InvalidArgumentError('Должен быть передан хотя бы один аргумент')
        base = TinkoffApiUrl
        for path in args:
            base = getattr(base, path)
        return base.url()


class TinkoffProfile:
    def __init__(self, token: str):
        self._session = requests.session()
        try:
            token.encode('latin-1')
        except (UnicodeEncodeError, AttributeError):
            raise InvalidTokenError('Неверный токен')
        self.token = token
        self.is_production_token_valid: bool = False
        self.is_sandbox_token_valid: bool = False
        self.broker_account_id: Optional[str] = None

    def auth(self, first='production') -> str:
        """ Авторизация по токену
        :param first: Какой метод авторизации будет первым (production/sandbox).
            Если авторизация не пройдет успешно, будет попытка вызвать другой метод
        """
        first = first.lower()
        methods = ('production', 'prod', 'sandbox', 'sand')
        if first not in methods:
            raise InvalidArgumentError(f'Передайте одно из следующих значений аргумента first: {", ".join(methods)}')

        url1 = TinkoffApiUrl.production.user.accounts.url()
        url2 = TinkoffApiUrl.sandbox.user.accounts.url()

        if first.startswith('sand'):
            url1, url2 = url2, url1

        for url in (url1, url2):
            response = self._session.get(
                url, headers={'Authorization': f'Bearer {self.token}'}
            )
            if response.status_code == 200:
                # FIXME: может быть несколько аккаунтов
                response_json = response.json()
                self.broker_account_id: str = response_json['payload']['accounts'][0]['brokerAccountId']
                self.is_sandbox_token_valid = self.broker_account_id.startswith('SB')
                self.is_production_token_valid = not self.is_sandbox_token_valid
                self._session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                return 'sandbox' if self.is_sandbox_token_valid else 'production'
            elif response.status_code in (401, 500):
                pass
        raise InvalidTokenError('Авторизация по токенам не удалась')

    @property
    def is_authorized(self) -> bool:
        return self.is_sandbox_token_valid or self.is_production_token_valid

    @only_authorized
    @generate_url
    def market_currencies(self, url: str):
        logger.info('Получение от Tinkoff API: market/currencies/')
        return self.response_to_json(self._session.get(url))

    @only_authorized
    @generate_url
    def market_stocks(self, url: str):
        return self.response_to_json(self._session.get(url))

    @only_authorized
    @generate_url
    def operations(self, from_datetime: dt.datetime, to_datetime: dt.datetime, url: str):
        """ Парсинг операций из tinkoff API в определенном временном интервале
        :param from_datetime: дата начала промежутка
        :param to_datetime: дата конца промежутка
        :param url: куда отправлять запрос
        :return: список операций
        """
        logger.info(f'Собираемся обновлять операции от {from_datetime.isoformat()} до {to_datetime.isoformat()}')
        self.check_date_range(from_datetime, to_datetime)
        response = self.response_to_json(self._session.get(
            url, data={
                'from': from_datetime.isoformat(),
                'to': to_datetime.isoformat()
            }
        ))
        logger.info('Операции получены')
        return response

    @staticmethod
    def check_date_range(from_datetime: dt.datetime, to_datetime: dt.datetime) -> True:
        """ Проверка дат на корректность.
            from_datetime должна быть меньше to_datetime,
            обе даты должны быть типа datetime, и иметь timezone
        :param from_datetime: начало промежутка
        :param to_datetime: конец промежутка
        :return: True или raise InvalidArgumentError
        """
        logger.info(f'Проверка валидности двух дат: {from_datetime} и {to_datetime}')
        if not (isinstance(from_datetime, dt.datetime) and isinstance(to_datetime, dt.datetime)):
            raise InvalidArgumentError('Аргументы from_datetime и to_datetime должны быть типа datetime')
        if from_datetime >= to_datetime:
            raise InvalidArgumentError('Аргумент from_datetime должен быть меньше аргумента to_datetime')
        if getattr(from_datetime, 'tzinfo', None) is None or getattr(to_datetime, 'tzinfo', None) is None:
            raise InvalidArgumentError('Аргументы from_datetime и to_datetime должны быть с timezone')
        if from_datetime.tzinfo != to_datetime.tzinfo:
            raise InvalidArgumentError('Временная зона должна быть одинаковой')
        if not (callable(getattr(from_datetime, 'isoformat', None)) and
                callable(getattr(to_datetime, 'isoformat', None))):
            raise InvalidArgumentError('Аргументы from_datetime и to_datetime должны иметь метод isoformat')
        logger.info('Даты валидны')

    @only_authorized
    @generate_url
    def portfolio(self, url: str):
        return self.response_to_json(self._session.get(url))

    @only_authorized
    @generate_url
    def portfolio_currencies(self, url: str):
        return self.response_to_json(self._session.get(url))

    def response_to_json(self, response):
        if response.status_code == 200:
            return response.json()
        elif response.status_code in (401, 500):
            raise UnauthorizedError('Токен не действителен')
        else:
            raise UnknownError(f'Неизвестный status_code запроса: {response.status_code}')

    def close(self):
        self._session.close()

    def __enter__(self):
        if not self.is_authorized:
            self.auth()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __str__(self):
        return f'{self.__class__.__name__} (auth={self.auth()})'
