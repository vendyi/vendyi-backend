import uuid

def generate_order_number():
    unique_id = uuid.uuid4().hex[:8]  # use the first 8 characters
    return f"ORD-{unique_id.capitalize()}"