# translations.py
"""Translation strings for Nova Poshta Tracking"""

TRANSLATIONS = {
    'en': {
        'dashboard': 'Dashboard', 'packages': 'Packages', 'settings': 'Settings',
        'logout': 'Logout', 'change_password': 'Change Password', 'admin': 'Admin',
        'users': 'Users', 'api_keys': 'API Keys', 'add_api_key': 'Add API Key',
        'add_user': 'Add User', 'total_packages': 'Total Packages', 'active': 'Active',
        'ready_pickup': 'Ready for Pickup', 'delivering': 'Delivering', 'delivered': 'Delivered',
        'last_sync': 'Last Sync', 'status': 'Status', 'actions': 'Actions', 'sync': 'Sync',
        'view': 'View', 'never': 'Never', 'incoming': 'Incoming', 'outgoing': 'Outgoing',
        'all': 'All', 'filters': 'Filters', 'direction': 'Direction', 'date_range': 'Date Range',
        'apply': 'Apply', 'reset': 'Reset', 'cancel': 'Cancel', 'sender': 'Sender',
        'recipient': 'Recipient', 'created': 'Created', 'save': 'Save Settings',
        'theme': 'Theme', 'light': 'Light', 'dark': 'Dark', 'view_mode': 'View Mode',
        'table': 'Table', 'cards': 'Cards', 'items_per_page': 'Items per page',
        'notify_pickup': 'Notify when ready for pickup', 'track_apis': 'Tracked API Keys',
        'language': 'Language', 'timezone': 'Timezone',
        'package_cost': 'Package Cost', 'shipping_cost': 'Shipping Cost', 'weight': 'Weight',
        'planned_delivery': 'Planned Delivery', 'description': 'Description',
        'no_packages': 'No packages found', 'no_api_keys': 'No API keys configured',
        'syncing': 'Syncing...', 'sync_success': 'Sync successful!', 'error': 'Error',
        'label': 'Label', 'sender_identifier': 'Sender Identifier', 'auto_sync': 'Auto Sync',
        'username': 'Username', 'full_name': 'Full Name', 'role': 'Role',
        'password': 'Password', 'new_password': 'New Password',
        'confirm_password': 'Confirm Password', 'current_password': 'Current Password',
        'save_changes': 'Save Changes', 'create_user': 'Create User',
        'inactive': 'Inactive', 'last_login': 'Last Login', 'edit': 'Edit',
        'login': 'Login', 'remember_me': 'Remember me (30 days)', 'sign_in': 'Sign In',
        'tracking_system': 'Package Tracking System',
        'no_account': 'No account? Contact administrator.',
        'days_1': 'Last 24 hours', 'days_5': 'Last 5 days', 'days_7': 'Last 7 days',
        'days_14': 'Last 14 days', 'days_30': 'Last 30 days', 'all_time': 'All time',
        'sync_all': 'Sync All', 'import_api_keys': 'Import', 'export_api_keys': 'Export',
        'author': 'Author',
        'in_transit': 'In Transit',
        'at_branch': 'At Branch',
        'completed': 'Completed',
        'package_trends': 'Package Trends',
        'last_30_days': 'Last 30 Days',
        'click_legend_to_toggle': 'Click legend items to toggle visibility',
        'invoice': 'Invoice',
        'details': 'Details',
        'close': 'Close',
        'save_as_draft': 'Save as Draft',
        'send': 'Send',
        'draft_saved': 'Draft saved!',

        # API Key
        'api_key': 'API Key',
        'select_api_key': 'Select API key',
        'incomplete_uuids': 'incomplete UUIDs - fetch required',
        
        # Sender
        'sender_your_company': 'Sender (Your Company)',
        'sender_city': 'Sender City',
        'sender_warehouse': 'Sender Warehouse',
        'edit_sender_location_once': 'Edit sender location for this package only',
        'start_typing': 'Start typing',
        
        # Client Selection
        'quick_select_client': 'Quick Select Client',
        'new_client': 'New client',
        'select_recent_or_create': 'Select from recent clients or create new',
        
        # Recipient (already have most, adding missing ones)
        'cyrillic_only_hint': 'Only Ukrainian letters (Cyrillic only)',
        'phone_10_digits': '10 digits starting with 0',
        'optional': 'Optional',
        'if_different_from_recipient': 'If different from recipient name',
        'save_client_for_later': 'Save this client for quick selection later',
        
        # Package Details
        'total_weight_all_seats': 'Total Weight',
        'declared_value_uah': 'Declared Value (UAH)',
        'dimensions_hint': 'Length × Width × Height in cm, Weight in kg',
        'package_description_placeholder': 'Brief description of package contents',
        'estimated_shipping_calculated': 'Estimated shipping cost: ~80 UAH (calculated by Nova Poshta)',
        'view_invoice': 'View Invoice',        
        'remove_deleted_package': 'Remove deleted package',
        'invoice_not_available_reason': 'Invoice only available for packages in transit',

        # Package Creation Modal
        'create_package': 'Create Package',
        'package_details': 'Package Details',
        'recipient_information': 'Recipient Information',
        'sender_information': 'Sender Information',
        'package_dimensions': 'Package Dimensions',
        
        # Recipient Fields
        'recipient_name': 'Recipient Name',
        'recipient_phone': 'Recipient Phone',
        'recipient_city': 'Recipient City',
        'recipient_warehouse': 'Warehouse',
        'recipient_contact': 'Contact Person',
        'search_city': 'Search city...',
        'select_city_first': 'Select city first...',
        'start_typing_city': 'Start typing city name...',
        
        # Package Fields
        'description': 'Description',
        'package_description': 'Package Description',
        'cost': 'Cost',
        'declared_value': 'Declared Value',
        'weight': 'Weight',
        'total_weight': 'Total Weight',
        'payment_method': 'Payment Method',
        'payer_type': 'Payer',
        'cargo_type': 'Cargo Type',
        
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
        
        
        # Client Management
        'save_client': 'Save client for future use',
        'recent_clients': 'Recent Clients',
        'quick_fill': 'Quick Fill',
        'select_client': 'Select Client',
        'new_client_spaceholder': '-- New client --',
        
        # Actions
        'create': 'Create',        
        'cancel': 'Cancel',
        'close': 'Close',
        'submit': 'Submit',

        #Draft Actions
        'save_as_draft': 'Save as Draft',
        'edit_draft': 'Edit Draft',
        'update_draft': 'Update & Send',
        'draft_updated': 'Draft updated successfully!',
        'error_loading_draft': 'Error loading draft',
        'delete_draft': 'Delete draft',
        
        # Payment Methods
        'cash': 'Cash',
        'non_cash': 'Non-Cash',
        
        # Payer Types
        'sender': 'Sender',
        'recipient': 'Recipient',
        
        # Cargo Types
        'parcel': 'Parcel',
        'documents': 'Documents',
        'cargo': 'Cargo',
        
        # Validation and alert Messages
        'contact_person_cyrillic_only': 'Contact person: use only Cyrillic characters',
        'please_select_api_key': 'Please select an API key',
        'please_select_city': 'Please select a city from the dropdown',
        'please_select_warehouse': 'Please select a warehouse',
        'recipient_name_required': 'Recipient name is required',
        'recipient_phone_required': 'Recipient phone is required',
        'add_at_least_one_seat': 'Please add at least one seat with weight',
        'cyrillic_only': 'Use only Cyrillic characters',
        'error_api_key_not_found': 'Error: API key select element not found',
        'package_created': 'Package created!',
        'error': 'Error',
        'unknown_error': 'Unknown error',
        'failed': 'Failed',
        
        # Success/Error Messages
        'package_created': 'Package created successfully!',
        'package_created_ttn': 'Package created! TTN: {ttn}',
        'saved_as_draft': 'Saved as draft',
        'api_error': 'API Error',
        'error_creating_package': 'Error creating package',
        'draft_saved': 'Package saved as draft',
        
        # Status Messages
        'creating_package': 'Creating package...',
        'fetching_uuids': 'Fetching recipient data...',
        'loading_clients': 'Loading clients...',
        'loading_warehouses': 'Loading warehouses...',
    },
    'uk': {
        'dashboard': 'Головна', 'packages': 'Посилки', 'settings': 'Налаштування',
        'logout': 'Вихід', 'change_password': 'Змінити пароль', 'admin': 'Адмін',
        'users': 'Користувачі', 'api_keys': 'API Ключі', 'add_api_key': 'Додати API',
        'add_user': 'Додати користувача', 'total_packages': 'Усього посилок',
        'active': 'Активні', 'ready_pickup': 'Готові до отримання',
        'delivering': 'Доставляються', 'delivered': 'Доставлені',
        'last_sync': 'Остання синхронізація', 'status': 'Статус', 'actions': 'Дії',
        'sync': 'Синхронізувати', 'view': 'Переглянути', 'never': 'Ніколи',
        'incoming': 'Вхідні', 'outgoing': 'Вихідні', 'all': 'Усі',
        'filters': 'Фільтри', 'direction': 'Напрямок', 'date_range': 'Період',
        'apply': 'Застосувати', 'reset': 'Скинути', 'cancel': 'Скасувати',
        'sender': 'Відправник', 'recipient': 'Отримувач', 'created': 'Створено',
        'save': 'Зберегти', 'theme': 'Тема', 'light': 'Світла', 'dark': 'Темна',
        'view_mode': 'Режим перегляду', 'table': 'Таблиця', 'cards': 'Картки',
        'items_per_page': 'Елементів на сторінці',
        'notify_pickup': 'Сповіщати при готовності', 'track_apis': 'Відстежувані API',
        'language': 'Мова', 'timezone': 'Часовий пояс',
        'package_cost': 'Вартість', 'shipping_cost': 'Доставка', 'weight': 'Вага',
        'planned_delivery': 'Планова доставка', 'description': 'Опис',
        'no_packages': 'Посилок не знайдено', 'no_api_keys': 'API ключі відсутні',
        'syncing': 'Синхронізація...', 'sync_success': 'Успішно!', 'error': 'Помилка',
        'label': 'Назва', 'sender_identifier': 'Ідентифікатор',
        'auto_sync': 'Авто синхронізація', 'username': 'Логін',
        'full_name': "Повне ім'я", 'role': 'Роль', 'password': 'Пароль',
        'new_password': 'Новий пароль', 'confirm_password': 'Підтвердити',
        'current_password': 'Поточний пароль', 'save_changes': 'Зберегти зміни',
        'create_user': 'Створити', 'inactive': 'Неактивний',
        'last_login': 'Останній вхід', 'edit': 'Редагувати', 'login': 'Вхід',
        'remember_me': "Запам'ятати (30 днів)", 'sign_in': 'Увійти',
        'tracking_system': 'Система відстеження', 'no_account': 'Зверніться до адміна.',
        'days_1': '24 години', 'days_5': '5 днів', 'days_7': '7 днів',
        'days_14': '14 днів', 'days_30': '30 днів', 'all_time': 'Весь час',
        'sync_all': 'Синхр. все', 'import_api_keys': 'Імпорт', 'export_api_keys': 'Експорт',
        'author': 'Автор',
        'in_transit': 'В дорозі',
        'at_branch': 'У відділенні',
        'completed': 'Доставлені',
        'package_trends': 'Тренди посилок',
        'last_30_days': 'Останні 30 днів',
        'click_legend_to_toggle': 'Виберіть елементи легенди, які бажаєте відобразити',
        'invoice': 'Накладна',
        'details': 'Детально',
        'close': 'Закрити',
        'save_as_draft': 'Зберегти як чернетку',
        'send': 'Відправити',
        'draft_saved': 'Чернетку збережено!',

        # API Key
        'api_key': 'API ключ',
        'select_api_key': 'Оберіть API ключ',
        'incomplete_uuids': 'неповні UUID - потрібно отримати',
        
        # Sender
        'sender_your_company': 'Відправник (Ваша компанія)',
        'sender_city': 'Місто відправника',
        'sender_warehouse': 'Відділення відправника',
        'edit_sender_location_once': 'Змінити локацію відправника тільки для цієї посилки',
        'start_typing': 'Почніть вводити',
        
        # Client Selection
        'quick_select_client': 'Швидкий вибір клієнта',
        'new_client': 'Новий клієнт',
        'select_recent_or_create': 'Оберіть з останніх клієнтів або створіть нового',
        
        # Recipient
        'cyrillic_only_hint': 'Тільки українські літери (лише кирилиця)',
        'phone_10_digits': '10 цифр, починаючи з 0',
        'optional': 'Необов\'язково',
        'if_different_from_recipient': 'Якщо відрізняється від імені отримувача',
        'save_client_for_later': 'Зберегти цього клієнта для швидкого вибору пізніше',
        
        # Package Details
        'total_weight_all_seats': 'Загальна вага',
        'declared_value_uah': 'Оголошена вартість (грн)',
        'dimensions_hint': 'Довжина × Ширина × Висота в см, Вага в кг',
        'package_description_placeholder': 'Короткий опис вмісту посилки',
        'estimated_shipping_calculated': 'Орієнтовна вартість доставки: ~80 грн (розраховується Новою Поштою)',
        'view_invoice': 'Переглянути накладну',
        'delete_draft': 'Видалити чернетку',
        'remove_deleted_package': 'Видалити посилку',
        'invoice_not_available_reason': 'Накладна доступна тільки для посилок у дорозі',

        # Package Creation Modal
        'create_package': 'Створити посилку',
        'package_details': 'Деталі посилки',
        'recipient_information': 'Інформація про отримувача',
        'sender_information': 'Інформація про відправника',
        'package_dimensions': 'Габарити посилки',
        
        # Recipient Fields
        'recipient_name': "Ім'я отримувача",
        'recipient_phone': 'Телефон отримувача',
        'recipient_city': 'Місто отримувача',
        'recipient_warehouse': 'Відділення',
        'recipient_contact': 'Контактна особа',
        'search_city': 'Пошук міста...',
        'select_city_first': 'Спочатку оберіть місто...',
        'start_typing_city': 'Почніть вводити назву міста...',
        
        # Package Fields
        'description': 'Опис',
        'package_description': 'Опис посилки',
        'cost': 'Вартість',
        'declared_value': 'Оголошена вартість',
        'weight': 'Вага',
        'total_weight': 'Загальна вага',
        'payment_method': 'Спосіб оплати',
        'payer_type': 'Платник',
        'cargo_type': 'Тип вантажу',
        
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
        'volumetric_weight': 'Об\'ємна вага',
        'volumetric_weight_example': 'Д×Ш×В÷4000',
        'auto_calculated': 'Авто-розрахунок',
        'sum_of_seats': 'Сума ваги всіх місць',
        
        # Client Management
        'save_client': 'Зберегти клієнта для майбутнього використання',
        'recent_clients': 'Останні клієнти',
        'quick_fill': 'Швидке заповнення',
        'select_client': 'Оберіть клієнта',
        'new_client_spaceholder': '-- Новий клієнт --',
        
        # Actions
        'create': 'Створити',
        'cancel': 'Скасувати',
        'close': 'Закрити',
        'submit': 'Відправити',

        #Draft Actions
        'save_as_draft': 'Зберегти як чернетку',
        'edit_draft': 'Редагувати чернетку',
        'update_draft': 'Оновити і відправити',
        'draft_updated': 'Чернетку успішно оновлено!',
        'error_loading_draft': 'Помилка завантаження чернетки',
        'delete_draft': 'Видалити чернетку',
        
        # Payment Methods
        'cash': 'Готівка',
        'non_cash': 'Безготівковий',
        
        # Payer Types
        'sender': 'Відправник',
        'recipient': 'Отримувач',
        
        # Cargo Types
        'parcel': 'Посилка',
        'documents': 'Документи',
        'cargo': 'Вантаж',
        
        # Validation and Alert Messages
        'contact_person_cyrillic_only': 'Контактна особа: використовуйте тільки кириличні символи',
        'please_select_api_key': 'Будь ласка, оберіть API ключ',
        'please_select_city': 'Будь ласка, оберіть місто зі списку',
        'please_select_warehouse': 'Будь ласка, оберіть відділення',
        'recipient_name_required': "Ім'я отримувача обов'язкове",
        'recipient_phone_required': 'Телефон отримувача обов\'язковий',
        'add_at_least_one_seat': 'Будь ласка, додайте хоча б одне місце з вагою',
        'cyrillic_only': 'Використовуйте тільки кириличні символи',
        'error_api_key_not_found': 'Помилка: не знайдено елемент вибору API ключа',
        'package_created': 'Посилку створено!',
        'error': 'Помилка',
        'unknown_error': 'Невідома помилка',
        'failed': 'Невдало',
        
        # Success/Error Messages
        'package_created': 'Посилку успішно створено!',
        'package_created_ttn': 'Посилку створено! ТТН: {ttn}',
        'saved_as_draft': 'Збережено як чернетку',
        'api_error': 'Помилка API',
        'error_creating_package': 'Помилка створення посилки',
        'draft_saved': 'Посилку збережено як чернетку',
        
        # Status Messages
        'creating_package': 'Створення посилки...',
        'fetching_uuids': 'Отримання даних отримувача...',
        'loading_clients': 'Завантаження клієнтів...',
        'loading_warehouses': 'Завантаження відділень...',
    }
}