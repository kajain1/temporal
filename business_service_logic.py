from dataclasses import dataclass
import uuid
import requests

## Custom retryable and non retryable exceptions extending Exception
class InvalidCardErrorNoRetry(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NotEnoughBalanceNoRetry(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


## Creating a mock payment system
class Card:
    def __init__(self, card_number: str, balance: float) -> None:
        self.card_number = card_number
        self.balance = balance

class PaymentSystem:
    def __init__(self, cards: list[Card]) -> None:
        self.cards = cards

    def find_card(self, card_number: str) -> Card:
        for card in self.cards:
            if card.card_number == card_number:
                return card
        raise InvalidCardErrorNoRetry(f"The card number {card_number} doesnt exist in payment system")


## Business/Services functions
@dataclass
class TxnProcessingSteps:

 ##Realtime API
    ## Creating a instance of mock payment system
    def __init__(self):
        self.mock_payment_api: PaymentSystem = PaymentSystem(
        [
            Card("1212 1212 1212 1212", 2000),
            Card("2323 2323 2323 2323", 0),
        ]
    )

    ## Function for checking if the card is valid and has enough balance
    def check_balance(self, card_number:str, amount:float) -> str:
        try:
            card = self.mock_payment_api.find_card(card_number)
            if amount > card.balance:
                raise NotEnoughBalanceNoRetry(f"The card number {card_number} has insufficient funds")
            else:
                return f"BalanceConfirmationId-{uuid.uuid4()}"
        except Exception:
            raise


    ## Function for processing payment
    def process_payment(self,card_number:str, amount:float, cart_id:str, cust_id: str) -> str:
        print(f"Passing-{cart_id}-{cust_id} for idempotency during payment processing; this will avoid double charge if payment process is retried for the same cart-id")
        return f"PaymentConfirmationId-{uuid.uuid4()}"

    ## Function for submitting order to the fulfillment system
    def submit_order(self,cart_id:str,store_num:str,product: str) -> str:
        ## Mocking a failure in submit order to initiate the refund process
        if store_num == "MockSubmitOrderFailure":
            raise Exception("Issue in submitting the order; Payment refund will be initiated")
        else:
            return f"TxnId-{uuid.uuid4()}"


    ## Function for processing refund when submit order fails
    def refund_payment(self, payment_confirmation_id:str) -> str:
        return f"Refund Processed for {payment_confirmation_id}"


 ##Post Processing Queue

    ## Function for getting customer's email using customer_id
    def customer_service(self,cust_id: str) -> str:
        url = f"https://dml8j.wiremockapi.cloud/customers/{cust_id}"
        try:
            response = requests.get(url)
            if (response.status_code == 404):
                raise Exception(f"The record for customer_id {cust_id} is not found. possibly due to data replication. keep retrying")
            else:
                return response.json()['email_address']
        except Exception:
            raise

    ## Function for sending receipt email to customer
    def send_email_receipt(self,email_address:str) -> str:
        return f"Sent receipt of your order to {email_address}"

 ## Function for sending offer email to customer
    def send_email_offer(self,email_address:str) -> str:
        return f"Sent offer email to {email_address}"
