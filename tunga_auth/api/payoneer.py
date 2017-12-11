# -*- coding: utf-8 -*-

"""
This performs api requests to the payoneer and performs appropriate
actions like;
   
   * Generating signup url.
"""
import requests

from tunga.settings import PAYONEER_API_URL

try:
    import simplejson as json
except ImportError as e:
    import json
import re
from bs4 import BeautifulSoup


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

    def __init__(self, username, password, client_id, client_payee_id):
        """
        Initiate and object to handle request to the payoneer system.
        
        @param: username  Client's account username assigned by Payoneer (provided upon setup of the client’s account profile).
        @param: password  Client's unique password assigned by Payoneer (provided upon setup of the client’s account profile).
        @param: client_id Client's unique ID assigned by Payoneer. 
        @param: client_payee_id: Payee’s Unique ID as used within the client's system.
        """

        self.mname = "GetToken"  # Kind of method name
        self.auto_pop_mname = "GetTokenXML"
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_payee_id = client_payee_id

    def _request_params(self, ret_dict=True, xml_payload=None):
        """
        Returns well formated parameters. used to pass
        to our request.
        
        if(ret_dict):
            @return payload and dictionary
        else:
            @return mname=GetToken&p1=wangoloj@outlook.com&p2=6935@Joel&p3=18141913&p4=18141913
        """
        try:
            if ret_dict and xml_payload:
                return {"mname": self.mname, "p1": self.username, "p2": self.password, "p3": self.client_id,
                        "xml": xml_payload}
            elif ret_dict and not xml_payload:
                return {"mname": self.mname, "p1": self.username, "p2": self.password, "p3": self.client_id,
                        "p4": self.client_payee_id}
            else:
                return "mname={}&p1={}&p2={}&p3={}&p4={}".format(self.mname, self.username, self.password,
                                                                 self.client_id, self.client_payee_id)
        except Exception as e:
            return {}

    def initiate_request(self, payload=None, headers=None):
        """
        Performs an initial request to the payeer and
        performs a post to request signup url.
        
        @param: payload
        """
        try:
            # Set the default method

            payload = payload if payload else self._request_params()
            headers = headers if headers else self.DEFAULT_HEADERS

            response = requests.post(self.PAYONEER_API_URL, data=payload, headers=headers)
            return self.parse_response(response)
        except Exception as e:
            raise

    def initiate_auto_populate(self, payload=None, headers=None, xml_payload=None):
        """
        Performs an initial request to the payoneer
        while adding in some auto populate features.
        
        @param payload --> xml payload
        """
        try:
            self.mname = self.auto_pop_mname
            payload = payload if payload else self._request_params(True, xml_payload)
            headers = headers if headers else self.DEFAULT_HEADERS

            response = requests.post(self.PAYONEER_API_URL, data=payload, headers=headers)
            return self.parse_response(response, True)

        except Exception as e:
            raise

    def parse_response(self, response, response_is_xml=False):
        """
        Parses response from the server.
        This includes 
            * Checking for errors
            * Parsing for xml if it's the response.
        """
        try:
            # Check if we have a valid url.
            regex = re.compile(
                r'^(?:http|ftp)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE
            )

            if regex.match(response.text):
                return {"payoneer_url": response.text}
            else:
                if response_is_xml:
                    # The response by default is xml
                    response_status = {}
                    soup = BeautifulSoup(response.text, "lxml")

                    token = soup.findAll("token")
                    if token:
                        response_status["payoneer_url"] = token[0].text
                        return response_status
                    else:
                        return {}
                else:
                    # Even this one is xml but it's a little different.
                    error_status = {}

                    # parse the xml response
                    soup = BeautifulSoup(response.text, "lxml")

                    code_status = soup.findAll("code")
                    if code_status:
                        error_status["code"] = code_status[0].text

                    error_description = soup.findAll("description")
                    if error_description:
                        error_status["description"] = error_description[0].text

                    return error_status

        except Exception as e:
            raise


class TungaPayoneerIPCN(TungaPayoneer):
    """
    Extends from TungaPayoneer to implement
    IPCN -> Instant Process Completion Notification.
    """

    def __init__(self, username, password, client_id):
        super(TungaPayoneerIPCN, self).__init__(username, password, client_id)
