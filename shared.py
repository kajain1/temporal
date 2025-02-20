from dataclasses import dataclass

ORDER_PROCESSING_TASK_QUEUE_NAME = "TQ_SBUX_ORDER_PROCESSING"
ASYNC_ORDER_PROCESSING_TASK_QUEUE_NAME = "ASYNC_TQ_SBUX_ORDER_PROCESSING"

@dataclass
class CartInfo:
    cart_id:str
    store_num:str
    product: str
    amount: float
    card_number: str
    cust_id: str