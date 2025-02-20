import asyncio
import traceback
import uuid
from workflows import ProcessCartWorkflow
from temporalio.client import Client, WorkflowFailureError
from shared import ORDER_PROCESSING_TASK_QUEUE_NAME, CartInfo

async def submit_to_wf(data):
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")
    try:
        result = await client.execute_workflow(
            ProcessCartWorkflow.run_wf,
            data,
            id=data.cart_id + "-" + data.cust_id,
            task_queue=ORDER_PROCESSING_TASK_QUEUE_NAME,
        )
        print(result)
        return result

    except WorkflowFailureError:
        print("Got expected exception: ", traceback.format_exc())


if __name__ == "__main__":
    data: CartInfo = CartInfo(
        cart_id="cart-id-"+str(uuid.uuid4()),
        product="Impossible Sandwich",
        amount=5,
        card_number="1212 1212 1212 1212",
        cust_id="custid1",
        store_num="121212"
    )
    asyncio.run(submit_to_wf(data))



#payload for success
    data: CartInfo = CartInfo(
        cart_id="cart-id-"+str(uuid.uuid4()),
        product="Impossible Sandwich",
        amount=5,
        card_number="1212 1212 1212 1212",
        cust_id="custid1",
        store_num="121212"
    )


#payload for Non retryable InvalidCardError;
    data: CartInfo = CartInfo(
        cart_id="cart-id-"+str(uuid.uuid4()),
        product="Impossible Sandwich",
        amount=5,
        card_number="1212 1212 1212 XYXY",
        cust_id="custid1",
        store_num="121212"
    )

#payload for Non retryable NotEnoughBalance;
    data: CartInfo = CartInfo(
        cart_id="cart-id-"+str(uuid.uuid4()),
        product="Impossible Sandwich",
        amount=2500,
        card_number="1212 1212 1212 1212",
        cust_id="custid1",
        store_num="121212"
    )

 #payload for mocking the submit order failure and do the refund via try catch
    data: CartInfo = CartInfo(
        cart_id="cart-id-"+str(uuid.uuid4()),
        product="Impossible Sandwich",
        amount=5,
        card_number="1212 1212 1212 1212",
        cust_id="custid1",
        store_num="MockSubmitOrderFailure"
    )

#payload for indefinete retry in post processing; in order for post processing workflow to succeed, wiremock needs to be changed to return success
    data: CartInfo = CartInfo(
        cart_id="cart-id-"+str(uuid.uuid4()),
        product="Impossible Sandwich",
        amount=5,
        card_number="1212 1212 1212 1212",
        cust_id="custid5",
        store_num="121212"
    )