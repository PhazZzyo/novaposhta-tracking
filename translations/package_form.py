# translations/package_form.py
"""Create/edit package modal: sender, recipient, seats, drafts, validation"""

PACKAGE_FORM_TRANSLATIONS = {
	'en': {
		# API Key
		'api_key': 'API Key',
		'select_api_key': 'Select API key',
		'incomplete_uuids': 'incomplete UUIDs - fetch required',

		# Sender
		'sender': 'Sender',
		'sender_your_company': 'Sender (Your Company)',
		'sender_city': 'Sender City',
		'sender_warehouse': 'Sender Warehouse',
		'sender_information': 'Sender Information',
		'edit_sender_location_once': 'Edit sender location for this package only',
		'start_typing': 'Start typing',

		# Client Selection
		'quick_select_client': 'Quick Select Client',
		'new_client': 'New client',
		'select_recent_or_create': 'Select from recent clients or create new',
		'save_client': 'Save client for future use',
		'save_client_for_later': 'Save this client for quick selection later',
		'recent_clients': 'Recent Clients',
		'quick_fill': 'Quick Fill',
		'select_client': 'Select Client',
		'new_client_spaceholder': '-- New client --',

		# Recipient
		'recipient': 'Recipient',
		'recipient_information': 'Recipient Information',
		'recipient_name': 'Recipient Name',
		'recipient_phone': 'Recipient Phone',
		'recipient_city': 'Recipient City',
		'recipient_warehouse': 'Warehouse',
		'recipient_contact': 'Contact Person',
		'search_city': 'Search city...',
		'select_city_first': 'Select city first...',
		'start_typing_city': 'Start typing city name...',
		'cyrillic_only_hint': 'Only Ukrainian letters (Cyrillic only)',
		'phone_10_digits': '10 digits starting with 0',
		'if_different_from_recipient': 'If different from recipient name',

		# Package Creation Modal
		'create_package': 'Create Package',
		'package_details': 'Package Details',
		'package_dimensions': 'Package Dimensions',

		# Package Fields
		'package_description': 'Package Description',
		'cost': 'Cost',
		'declared_value': 'Declared Value',
		'declared_value_uah': 'Declared Value (UAH)',
		'total_weight': 'Total Weight',
		'total_weight_all_seats': 'Total Weight',
		'payment_method': 'Payment Method',
		'payer_type': 'Payer',
		'cargo_type': 'Cargo Type',
		'dimensions_hint': 'Length × Width × Height in cm, Weight in kg',
		'package_description_placeholder': 'Brief description of package contents',
		'estimated_shipping_calculated': 'Estimated shipping cost: ~80 UAH (calculated by Nova Poshta)',

		# Seats
		'seats': 'Seats',
		'seat': 'Seat',
		'number_of_seats': 'Number of Seats',
		'add_seat': 'Add Seat',
		'copy_seat': 'Copy',
		'delete_seat': 'Delete',
		'seat_weight': 'Weight (kg)',
		'seat_length': 'Length (cm)',
		'seat_width': 'Width (cm)',
		'seat_height': 'Height (cm)',
		'volumetric_weight': 'Volumetric Weight',
		'volumetric_weight_example': 'L×W×H÷4000',
		'auto_calculated': 'Auto-calculated',
		'sum_of_seats': 'Sum of all seat weights',

		# Draft Actions
		'save_as_draft': 'Save as Draft',
		'edit_draft': 'Edit Draft',
		'update_draft': 'Update & Send',
		'draft_updated': 'Draft updated successfully!',
		'error_loading_draft': 'Error loading draft',
		'delete_draft': 'Delete draft',
		'draft_saved': 'Package saved as draft',

		# Payment Methods
		'cash': 'Cash',
		'non_cash': 'Non-Cash',

		# Cargo Types
		'parcel': 'Parcel',
		'documents': 'Documents',
		'cargo': 'Cargo',

		# Validation / Alert Messages
		'contact_person_cyrillic_only': 'Contact person: use only Cyrillic characters',
		'please_select_api_key': 'Please select an API key',
		'please_select_city': 'Please select a city from the dropdown',
		'please_select_warehouse': 'Please select a warehouse',
		'recipient_name_required': 'Recipient name is required',
		'recipient_phone_required': 'Recipient phone is required',
		'add_at_least_one_seat': 'Please add at least one seat with weight',
		'cyrillic_only': 'Use only Cyrillic characters',
		'error_api_key_not_found': 'Error: API key select element not found',

		# Success/Error Messages
		'package_created': 'Package created successfully!',
		'package_created_ttn': 'Package created! TTN: {ttn}',
		'saved_as_draft': 'Saved as draft',
		'api_error': 'API Error',
		'error_creating_package': 'Error creating package',

		# Status Messages
		'creating_package': 'Creating package...',
		'fetching_uuids': 'Fetching recipient data...',
		'loading_clients': 'Loading clients...',
		'loading_warehouses': 'Loading warehouses...',
	},
	'uk': {
		# API Key
		'api_key': 'API ключ',
		'select_api_key': 'Оберіть API ключ',
		'incomplete_uuids': 'неповні UUID - потрібно отримати',

		# Sender
		'sender': 'Відправник',
		'sender_your_company': 'Відправник (Ваша компанія)',
		'sender_city': 'Місто відправника',
		'sender_warehouse': 'Відділення відправника',
		'sender_information': 'Інформація про відправника',
		'edit_sender_location_once': 'Змінити локацію відправника тільки для цієї посилки',
		'start_typing': 'Почніть вводити',

		# Client Selection
		'quick_select_client': 'Швидкий вибір клієнта',
		'new_client': 'Новий клієнт',
		'select_recent_or_create': 'Оберіть з останніх клієнтів або створіть нового',
		'save_client': 'Зберегти клієнта для майбутнього використання',
		'save_client_for_later': 'Зберегти цього клієнта для швидкого вибору пізніше',
		'recent_clients': 'Останні клієнти',
		'quick_fill': 'Швидке заповнення',
		'select_client': 'Оберіть клієнта',
		'new_client_spaceholder': '-- Новий клієнт --',

		# Recipient
		'recipient': 'Отримувач',
		'recipient_information': 'Інформація про отримувача',
		'recipient_name': "Ім'я отримувача",
		'recipient_phone': 'Телефон отримувача',
		'recipient_city': 'Місто отримувача',
		'recipient_warehouse': 'Відділення',
		'recipient_contact': 'Контактна особа',
		'search_city': 'Пошук міста...',
		'select_city_first': 'Спочатку оберіть місто...',
		'start_typing_city': 'Почніть вводити назву міста...',
		'cyrillic_only_hint': 'Тільки українські літери (лише кирилиця)',
		'phone_10_digits': '10 цифр, починаючи з 0',
		'if_different_from_recipient': 'Якщо відрізняється від імені отримувача',

		# Package Creation Modal
		'create_package': 'Створити посилку',
		'package_details': 'Деталі посилки',
		'package_dimensions': 'Габарити посилки',

		# Package Fields
		'package_description': 'Опис посилки',
		'cost': 'Вартість',
		'declared_value': 'Оголошена вартість',
		'declared_value_uah': 'Оголошена вартість (грн)',
		'total_weight': 'Загальна вага',
		'total_weight_all_seats': 'Загальна вага',
		'payment_method': 'Спосіб оплати',
		'payer_type': 'Платник',
		'cargo_type': 'Тип вантажу',
		'dimensions_hint': 'Довжина × Ширина × Висота в см, Вага в кг',
		'package_description_placeholder': 'Короткий опис вмісту посилки',
		'estimated_shipping_calculated': 'Орієнтовна вартість доставки: ~80 грн (розраховується Новою Поштою)',

		# Seats
		'seats': 'Кількість місць',
		'seat': 'Місце',
		'number_of_seats': 'Кількість місць',
		'add_seat': 'Додати місце',
		'copy_seat': 'Копіювати',
		'delete_seat': 'Видалити',
		'seat_weight': 'Вага (кг)',
		'seat_length': 'Довжина (см)',
		'seat_width': 'Ширина (см)',
		'seat_height': 'Висота (см)',
		'volumetric_weight': "Об'ємна вага",
		'volumetric_weight_example': 'Д×Ш×В÷4000',
		'auto_calculated': 'Авто-розрахунок',
		'sum_of_seats': 'Сума ваги всіх місць',

		# Draft Actions
		'save_as_draft': 'Зберегти як чернетку',
		'edit_draft': 'Редагувати чернетку',
		'update_draft': 'Оновити і відправити',
		'draft_updated': 'Чернетку успішно оновлено!',
		'error_loading_draft': 'Помилка завантаження чернетки',
		'delete_draft': 'Видалити чернетку',
		'draft_saved': 'Посилку збережено як чернетку',

		# Payment Methods
		'cash': 'Готівка',
		'non_cash': 'Безготівковий',

		# Cargo Types
		'parcel': 'Посилка',
		'documents': 'Документи',
		'cargo': 'Вантаж',

		# Validation / Alert Messages
		'contact_person_cyrillic_only': 'Контактна особа: використовуйте тільки кириличні символи',
		'please_select_api_key': 'Будь ласка, оберіть API ключ',
		'please_select_city': 'Будь ласка, оберіть місто зі списку',
		'please_select_warehouse': 'Будь ласка, оберіть відділення',
		'recipient_name_required': "Ім'я отримувача обов'язкове",
		'recipient_phone_required': "Телефон отримувача обов'язковий",
		'add_at_least_one_seat': 'Будь ласка, додайте хоча б одне місце з вагою',
		'cyrillic_only': 'Використовуйте тільки кириличні символи',
		'error_api_key_not_found': 'Помилка: не знайдено елемент вибору API ключа',

		# Success/Error Messages
		'package_created': 'Посилку успішно створено!',
		'package_created_ttn': 'Посилку створено! ТТН: {ttn}',
		'saved_as_draft': 'Збережено як чернетку',
		'api_error': 'Помилка API',
		'error_creating_package': 'Помилка створення посилки',

		# Status Messages
		'creating_package': 'Створення посилки...',
		'fetching_uuids': 'Отримання даних отримувача...',
		'loading_clients': 'Завантаження клієнтів...',
		'loading_warehouses': 'Завантаження відділень...',
	}
}