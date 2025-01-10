def load_context(user_id):
    # Загрузка инструкций
    with open('data/instructions.txt', 'r', encoding='utf-8') as file:
        instructions = file.read()

    # Загрузка прайс-листа
    with open('data/price_list.txt', 'r', encoding='utf-8') as file:
        price_list = file.read()

    # Загрузка описаний процедур
    with open('data/procedures.txt', 'r', encoding='utf-8') as file:
        procedures = file.read()

    # Загрузка информации о клиенте
    from handlers.database import get_client_messages
    messages = get_client_messages(user_id)
    client_history = "\n".join([f"Клиент: {msg.message_text}" for msg in messages])

    # Формирование контекста
    context = f"""

{price_list}

{client_history}
"""
    return context
