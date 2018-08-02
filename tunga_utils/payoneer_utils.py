# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

from tunga.settings import PAYONEER_API_URL, TUNGA_URL, PAYONEER_USERNAME, PAYONEER_PASSWORD, PAYONEER_PARTNER_ID
from tunga_utils.constants import CURRENCY_EUR


class TungaPayoneer(object):
    """
    Pure python wrapper to perform api requests to
    Payoneer
    """

    PAYONEER_API_URL = PAYONEER_API_URL
    DEFAULT_REQ_METHOD = "POST"

    DEFAULT_HEADERS = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    def __init__(self, username, password, client_id):
        """
        Initiate and object to handle request to the payoneer system.

        @param: username  Payoneer username
        @param: password  Payoneer password
        @param: client_id Payoneer partner id
        """
        self.username = username
        self.password = password
        self.client_id = client_id
        self.default_request_params = dict(p1=self.username, p2=self.password, p3=self.client_id)

    def _create_request_params(self, method, data=None, serialize=False):
        params = dict()
        params['mname'] = method
        params.update(self.default_request_params)
        if data and type(data) == dict:
            params.update(data)
        if serialize:
            return '&'.join(['{}={}'.format(key, params[key]) for key in params])
        return params

    def compose_sign_up_xml(self, data=None):
        """
        Construct XML for Sign Up Auto Populate
        """
        xml = (
            '''<?xml version="1.0" encoding="utf-8"?>
            <PayoneerDetails>
                <Details>
                    <prid></prid>
                    <apuid>{payee_id}</apuid>
                    <sessionid></sessionid>
                    <redirect>{redirect_url}</redirect>
                    <PayeeType>{payee_type}</PayeeType>
                    <redirectTime></redirectTime>
                    <PayoutMethodList></PayoutMethodList>
                    <RegMode></RegMode>
                 </Details>
                <PersonalDetails>
                    <firstName>{first_name}</firstName>
                    <lastName>{last_name}</lastName>
                    <dateOfBirth></dateOfBirth>
                    <address1></address1>
                    <address2></address2>
                    <city></city>
                    <country></country>
                    <state></state>
                    <zipCode></zipCode>
                    <mobile></mobile>
                    <phone>{phone_number}</phone>
                    <email>{email}</email>
                </PersonalDetails>
            </PayoneerDetails>'''
        ).encode('utf-8')

        if type(data) is not dict:
            data = dict()

        data['redirect_url'] = data.get('redirect_url', '{}/settings/payment/?status=pending'.format(TUNGA_URL))
        data['payee_type'] = data.get('payee_type', 1)

        for key in ['payee_id', 'first_name', 'last_name', 'phone_number', 'email']:
            data[key] = data.get(key, '')

        try:
            return xml.format(**data)
        except:
            return ''

    def _parse_xml_response(self, response, targets):
        """
        Parses XML response
        """
        results = dict()
        soup = BeautifulSoup(response, "lxml")

        for key in targets:
            token = soup.findAll(key)
            if token:
                results[key] = token[0].text

        if results:
            return results
        else:
            for key in ['code', 'description']:
                token = soup.findAll(key)
                if token:
                    results[key] = token[0].text
        return results

    def sign_up(self, payee_id, headers=None):
        """
        Sign Up
        """
        payload = self._create_request_params('GetToken', dict(p4=payee_id))

        response = requests.post(self.PAYONEER_API_URL, data=payload, headers=headers or self.DEFAULT_HEADERS)

        try:
            return self._parse_xml_response(response.text, ['token'])
        except:
            return

    def sign_up_auto_populate(self, payee_id, data, headers=None):
        """
        Sign Up Auto Populate
        """
        xml_data = dict(payee_id=payee_id)
        if type(data) is dict:
            xml_data.update(data)
        payload = self._create_request_params('GetTokenXML', dict(xml=self.compose_sign_up_xml(xml_data)))
        response = requests.post(self.PAYONEER_API_URL, data=payload, headers=headers or self.DEFAULT_HEADERS)

        try:
            return self._parse_xml_response(response.text, ['token'])
        except:
            return

    def get_balance(self, headers=None):
        """
        Get Balance
        """
        payload = self._create_request_params('GetAccountDetails')
        response = requests.post(self.PAYONEER_API_URL, data=payload, headers=headers or self.DEFAULT_HEADERS)

        try:
            return self._parse_xml_response(response.text, ['accountbalance', 'feesdue', 'curr'])
        except:
            return

    def make_payment(self, program_id, payment_id, payee_id, amount, description, currency=CURRENCY_EUR, headers=None):
        """
        Make Payment
        """
        payload = self._create_request_params(
            'PerformPayoutPayment', dict(
                p4=program_id, p5=payment_id, p6=payee_id, p7='{0:.2f}'.format(amount), p8=description, Currency=currency
            )
        )
        response = requests.post(self.PAYONEER_API_URL, data=payload, headers=headers or self.DEFAULT_HEADERS)

        try:
            return self._parse_xml_response(response.text, ['status', 'paymentid', 'payoneerid', 'description'])
        except:
            return


def get_client(username=PAYONEER_USERNAME, password=PAYONEER_PASSWORD, client_id=PAYONEER_PARTNER_ID):
    return TungaPayoneer(username, password, client_id)


def generate_error_redirect_url(
    status, message='Something went wrong! please try again.', url=None
):
    return '{}?status=error&message={}&status_code={}'.format(
        url or '{}/settings/payment/payoneer'.format(TUNGA_URL), message, status
    )
