from temporalio import activity
import asyncio
from shared import CartInfo
from business_service_logic import TxnProcessingSteps

## Creating activities for all business logic/services
class TxnProcessingActivities:
    def __init__(self):
        self.txn = TxnProcessingSteps()

    @activity.defn
    async def check_balance_activity(self, data: CartInfo) -> str:
        confirmation = await asyncio.to_thread(
            self.txn.check_balance, data.card_number, data.amount)
        return confirmation

    @activity.defn
    async def process_payment_activity(self, data: CartInfo) -> str:
        confirmation = await asyncio.to_thread(
            self.txn.process_payment, data.card_number, data.amount, data.cart_id, data.cust_id)
        return confirmation

    @activity.defn
    async def submit_order_activity(self, data: CartInfo) -> str:
        confirmation = await asyncio.to_thread(
            self.txn.submit_order, data.cart_id, data.store_num, data.product)
        return confirmation

    @activity.defn
    async def refund_payment_activity(self, payment_confirmation_id:str) -> str:
        confirmation = await asyncio.to_thread(
            self.txn.refund_payment, payment_confirmation_id)
        return confirmation

    @activity.defn
    async def customer_service_activity(self, data: CartInfo) -> str:
        confirmation = await asyncio.to_thread(
            self.txn.customer_service, data.cust_id)
        return confirmation

    @activity.defn
    async def send_email_receipt_activity(self,email_address:str) -> str:
        confirmation = await asyncio.to_thread(
            self.txn.send_email_receipt, email_address)
        return confirmation

    @activity.defn
    async def send_email_offer_activity(self,email_address:str) -> str:
        confirmation = await asyncio.to_thread(
            self.txn.send_email_offer, email_address)
        return confirmation