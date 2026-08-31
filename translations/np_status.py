# translations/np_status.py
"""
Official Nova Poshta tracking status code labels (uk/en), per documented
getStatusDocuments reference table (TrackingDocumentGeneral model).

Source: NP API documentation, "Трекінг" / getStatusDocuments status list.
"""

NP_STATUS_LABELS = {
	'1': {
		'uk': 'Відправник самостійно створив цю накладну, але ще не надав до відправки',
		'en': 'Sender created the waybill but has not yet handed over the package',
	},
	'2': {
		'uk': 'Видалено',
		'en': 'Deleted',
	},
	'3': {
		'uk': 'Номер не знайдено',
		'en': 'Number not found',
	},
	'4': {
		'uk': 'Відправлення у місті XXXX',
		'en': 'Package in city XXXX (inter-regional)',
	},
	'41': {
		'uk': 'Відправлення у місті XXXX (Локал стандарт/експрес)',
		'en': 'Package in city XXXX (Local standard/express, in-city delivery)',
	},
	'5': {
		'uk': 'Відправлення прямує до міста YYYY',
		'en': 'Package heading to city YYYY',
	},
	'6': {
		'uk': 'Відправлення у місті YYYY, орієнтовна доставка до відділення',
		'en': 'Package in city YYYY, estimated delivery to branch pending',
	},
	'7': {
		'uk': 'Прибув на відділення',
		'en': 'Arrived at branch',
	},
	'8': {
		'uk': 'Прибув на відділення (завантажено в Поштомат)',
		'en': 'Arrived at branch (loaded into parcel locker)',
	},
	'9': {
		'uk': 'Відправлення отримано',
		'en': 'Package received',
	},
	'10': {
		'uk': 'Відправлення отримано. Очікується SMS про грошовий переказ',
		'en': 'Package received. Cash-on-delivery SMS notification pending',
	},
	'11': {
		'uk': 'Відправлення отримано. Грошовий переказ видано одержувачу',
		'en': 'Package received. Cash-on-delivery payout completed',
	},
	'12': {
		'uk': 'Нова пошта комплектує ваше відправлення',
		'en': 'Nova Poshta is preparing your shipment',
	},
	'15': {
		'uk': 'Відправлення вже в дорозі до України',
		'en': 'Package en route to Ukraine (international)',
	},
	'101': {
		'uk': 'На шляху до одержувача',
		'en': 'On the way to recipient',
	},
	'102': {
		'uk': 'Відмова від отримання (відправником створено замовлення на повернення)',
		'en': 'Refused (sender initiated a return)',
	},
	'103': {
		'uk': 'Відмова від отримання',
		'en': 'Refused by recipient',
	},
	'104': {
		'uk': 'Змінено адресу',
		'en': 'Address changed',
	},
	'105': {
		'uk': 'Припинено зберігання',
		'en': 'Storage discontinued',
	},
	'106': {
		'uk': 'Одержано і створено ЕН зворотної доставки',
		'en': 'Received, return waybill created',
	},
	'107': {
		'uk': 'Переміщено з пункту видачі (PUDO) до основного відділення',
		'en': 'Moved from pickup point (PUDO) to main branch',
	},
	'111': {
		'uk': "Невдала спроба доставки: відсутність одержувача або зв'язку з ним",
		'en': 'Failed delivery attempt: recipient unavailable or unreachable',
	},
	'112': {
		'uk': 'Дата доставки перенесена одержувачем',
		'en': 'Delivery date postponed by recipient',
	},
}


def get_status_label(status_code, lang='uk'):
	"""
	Get a friendly, translated label for a Nova Poshta status code.
	Falls back to Ukrainian, then to a generic 'Status N' if unknown.
	"""
	entry = NP_STATUS_LABELS.get(str(status_code))
	if not entry:
		return f'Status {status_code}'
	return entry.get(lang, entry.get('uk', str(status_code)))
