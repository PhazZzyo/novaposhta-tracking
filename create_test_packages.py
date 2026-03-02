#!/usr/bin/env python3
"""
Create test packages for Ready for Pickup testing
Run in ~/np: python3 create_test_packages.py
"""

import sqlite3
from datetime import datetime

DB_PATH = 'instance/novaposhta.db'

print("🔧 Creating test packages...")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get first API key ID
cursor.execute("SELECT id FROM api_keys LIMIT 1")
api_key_id = cursor.fetchone()[0]

# Test packages data
test_packages = [
    {
        'tracking_number': '00000000000001',
        'direction': 'incoming',
        'status_code': '7',
        'status': 'Посилка прибула на відділення',
        'sender_name': 'Test Sender A',
        'sender_city': 'Київ',
        'recipient_name': 'Your Company',
        'recipient_city': 'Черкаси',
        'recipient_warehouse': 'Відділення №3',
        'recipient_warehouse_number': '3',
        'is_delivered': 0
    },
    {
        'tracking_number': '00000000000002',
        'direction': 'incoming',
        'status_code': '8',
        'status': 'Прибула на відділення (очікує до завтра)',
        'sender_name': 'Test Sender B',
        'sender_city': 'Львів',
        'recipient_name': 'Your Company',
        'recipient_city': 'Черкаси',
        'recipient_warehouse': 'Відділення №5',
        'recipient_warehouse_number': '5',
        'is_delivered': 0
    },
    {
        'tracking_number': '00000000000003',
        'direction': 'outgoing',
        'status_code': '7',
        'status': 'Посилка прибула на відділення (клієнт має забрати)',
        'sender_name': 'Your Company',
        'sender_city': 'Черкаси',
        'recipient_name': 'Test Customer C',
        'recipient_city': 'Одеса',
        'recipient_warehouse': 'Відділення №12',
        'is_delivered': 0
    },
    {
        'tracking_number': '00000000000004',
        'direction': 'incoming',
        'status_code': '9',
        'status': 'Отримано (тест)',
        'sender_name': 'Test Sender D',
        'sender_city': 'Харків',
        'recipient_name': 'Your Company',
        'recipient_city': 'Черкаси',
        'is_delivered': 1
    }
]

for pkg in test_packages:
    cursor.execute("""
        INSERT INTO packages (
            api_key_id, tracking_number, direction, status_code, status,
            sender_name, sender_city, recipient_name, recipient_city,
            recipient_warehouse, is_delivered,
            date_created, package_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        api_key_id,
        pkg['tracking_number'],
        pkg['direction'],
        pkg['status_code'],
        pkg['status'],
        pkg['sender_name'],
        pkg['sender_city'],
        pkg['recipient_name'],
        pkg['recipient_city'],
        pkg.get('recipient_warehouse'),
        pkg['is_delivered'],
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    print(f"✅ Created: {pkg['tracking_number']} - {pkg['status']}")

conn.commit()
conn.close()

print("\n" + "="*70)
print("✅ TEST PACKAGES CREATED!")
print("="*70)
print("""
CREATED:
1. TEST_INCOMING_STATUS7_001 - Incoming, Ready (status 7)
2. TEST_INCOMING_STATUS8_002 - Incoming, Ready (status 8)
3. TEST_OUTGOING_STATUS7_003 - Outgoing, Delivering (status 7)
4. TEST_INCOMING_DELIVERED_004 - Incoming, Delivered (status 9)

NOW TEST:
1. Refresh dashboard
2. Ready for Pickup card should show: 2
3. Click Ready → should show TEST_INCOMING_STATUS7 and STATUS8
4. Delivering should include TEST_OUTGOING_STATUS7
5. Delivered should include TEST_INCOMING_DELIVERED

To remove test packages later:
sqlite3 instance/novaposhta.db "DELETE FROM packages WHERE tracking_number LIKE '0000000000000_%';"
""")
print("="*70)
