import requests

# Замените на ваш локальный URL API
BASE_URL = 'http://127.0.0.1:8000/orders/'

# ID заказа, который вы хотите изменить
ORDER_ID = 14
# Получите текущий заказ
response = requests.get(f"{BASE_URL}{ORDER_ID}/")
order = response.json()

print(f"Current 'cooked' status: {order['cooked']}")

order['ready'] = True

response = requests.put(f"{BASE_URL}{ORDER_ID}/", json=order)

if response.status_code == 200:
    print("Order updated successfully!")
    updated_order = response.json()
    print(f"New 'cooked' status: {updated_order['cooked']}")
else:
    print(40444)