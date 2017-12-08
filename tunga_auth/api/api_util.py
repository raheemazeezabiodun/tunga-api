from tunga.settings import TUNGA_URL


def parse_default_xml_args(client_payee_id, firstname, lastname, phonenumber, p_type=1, redirect_url=None):
    """
    Constructs default args for the xml args to be 
    passed to requests.
    """

    xml = (
        '''<?xml version="1.0" encoding="utf-8"?>
        <PayoneerDetails>
            <Details>
                <prid></prid>
                <apuid>{}</apuid>
                <sessionid></sessionid>
                <redirect>{}</redirect>
                <PayeeType>{}</PayeeType>
                <redirectTime></redirectTime>
                <PayoutMethodList></PayoutMethodList>
                <RegMode></RegMode>
             </Details>
            <PersonalDetails>
                <firstName>{}</firstName>
                <lastName>{}</lastName>
                <dateOfBirth></dateOfBirth>
                <address1></address1>
                <address2></address2>
                <city></city>
                <country></country>
                <state></state>
                <zipCode></zipCode>
                <mobile></mobile>
                <phone>{}</phone>
                <email></email>
            </PersonalDetails>
        </PayoneerDetails>'''
    ).encode('utf-8')

    try:
        return xml.format(client_payee_id, redirect_url or '{}/profile/payment/payoneer'.format(TUNGA_URL), p_type, firstname, lastname, phonenumber)
    except Exception as e:
        return ''
