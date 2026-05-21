# services/novaposhta.py
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

NOVA_POSHTA_API = 'https://api.novaposhta.ua/v2.0/json/'


class NovaPoshtaAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        # Reuse session for all API requests
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def _post(self, model, method, props=None):
        payload = {
            'apiKey': self.api_key,
            'modelName': model,
            'calledMethod': method,
            'methodProperties': props or {}
        }
        # Use self.session instead of requests
        r = self.session.post(NOVA_POSHTA_API, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not data.get('success'):
            raise Exception(', '.join(data.get('errors', ['Unknown error'])))
        return data.get('data', []), data

    def __del__(self):
        """Close session when API object is destroyed"""
        try:
            self.session.close()
        except Exception:
            pass

    def get_documents_list(self, date_from, limit=100):
        return self._post('InternetDocument', 'getDocumentList', {
            'DateFrom': date_from.strftime('%d.%m.%Y'),
            'DateTo': datetime.now().strftime('%d.%m.%Y'),
            'Page': '1',
            'Limit': str(limit),
            'GetFullList': '1'
        })

    def get_incoming_documents(self, phone):
        """Get INCOMING packages by phone number (10 digits: 0XXXXXXXXX)"""
        if not phone:
            return [], {}
        phone = str(phone).strip()
        if len(phone) != 10 or not phone.startswith('0') or not phone.isdigit():
            raise Exception(f"Phone must be 10 digits (0XXXXXXXXX), got: {phone}")
        return self._post('InternetDocument', 'getIncomingDocumentsByPhone', {
            'Phone': phone
        })

    def create_internet_document(self, sender_data, recipient_data, package_data):
        """Create package via Nova Poshta API - requires UUIDs for all refs"""
        current_date = datetime.now(ZoneInfo("Europe/Kyiv")).strftime('%d.%m.%Y')
        payload = {
            'PayerType': package_data.get('payer_type', 'Recipient'),
            'PaymentMethod': package_data.get('payment_method', 'Cash'),
            'DateTime': current_date,
            'CargoType': package_data.get('cargo_type', 'Parcel'),
            'Weight': str(package_data['weight']),
            'ServiceType': 'WarehouseWarehouse',
            'SeatsAmount': str(package_data.get('seats_amount', 1)),
            'Description': package_data['description'],
            'Cost': str(package_data['cost']),
            # Sender
            'CitySender': sender_data['city_ref'],
            'Sender': sender_data['counterparty_ref'],
            'SenderAddress': sender_data['warehouse_ref'],
            'ContactSender': sender_data['contact_ref'],
            'SendersPhone': sender_data['phone'],
            # Recipient
            'CityRecipient': recipient_data['city_ref'],
            'Recipient': recipient_data['counterparty_ref'],
            'RecipientAddress': recipient_data['warehouse_ref'],
            'ContactRecipient': recipient_data['contact_ref'],
            'RecipientsPhone': recipient_data['phone'],
            'RecipientName': recipient_data.get('name', ''),
            'RecipientType': 'PrivatePerson'
        }
        if package_data.get('seats_data'):
            payload['OptionsSeat'] = package_data['seats_data']
        print(f"📨 Full API payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        return self._post('InternetDocument', 'save', payload)

    def search_cities(self, query):
        """Search cities by name"""
        return self._post('Address', 'getCities', {
            'FindByString': query,
            'Limit': '20'
        })

    def get_warehouses(self, city_ref):
        """Get warehouses in city"""
        return self._post('Address', 'getWarehouses', {
            'CityRef': city_ref,
            'Limit': '100'
        })

    def create_or_get_recipient(self, name, phone):
        """
        Create or find recipient counterparty
        Returns: {'counterparty_ref': '...', 'contact_ref': '...'}
        """
        name_parts = name.strip().split()
        first_name = name_parts[0] if len(name_parts) > 0 else name
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        middle_name = ' '.join(name_parts[1:-1]) if len(name_parts) > 2 else ''

        result, response = self._post('Counterparty', 'save', {
            'CounterpartyType': 'PrivatePerson',
            'CounterpartyProperty': 'Recipient',
            'FirstName': first_name,
            'LastName': last_name,
            'MiddleName': middle_name,
            'Phone': phone
        })

        if not result or len(result) == 0:
            error_msg = response.get('errors', ['Unknown error'])[0] if response.get('errors') else 'No data returned'
            raise Exception(f'Failed to create recipient: {error_msg}')

        recipient_data = result[0]
        counterparty_ref = recipient_data.get('Ref')
        contact_person_data = recipient_data.get('ContactPerson', {}).get('data', [])
        contact_ref = contact_person_data[0].get('Ref') if contact_person_data else None

        if not counterparty_ref or not contact_ref:
            raise Exception('Response missing Ref or ContactPerson.Ref')

        return {
            'counterparty_ref': counterparty_ref,
            'contact_ref': contact_ref
        }

    def get_status_documents(self, tracking_numbers):
        """Get status for multiple tracking numbers"""
        if not tracking_numbers:
            return [], {}
        documents = [{'DocumentNumber': str(tn)} for tn in tracking_numbers[:100]]
        return self._post('TrackingDocument', 'getStatusDocuments', {'Documents': documents})

    def get_counterparty_documents(self, counterparty_ref, date_from, limit=100):
        return self._post('InternetDocument', 'getDocumentList', {
            'CounterpartyRef': counterparty_ref,
            'DateFrom': date_from.strftime('%d.%m.%Y'),
            'DateTo': datetime.now().strftime('%d.%m.%Y'),
            'Page': '1',
            'Limit': str(limit),
            'GetFullList': '1'
        })


def _parse_dt(s, fmt='%Y-%m-%d %H:%M:%S'):
    try:
        return datetime.strptime(s, fmt) if s and s != '0001-01-01 00:00:00' else None
    except Exception:
        return None


def is_delivered(status_code):
    """Delivered: status codes 2 (deleted), 9, 10, or 11"""
    return str(status_code).strip() in ['2', '9', '10', '11']
