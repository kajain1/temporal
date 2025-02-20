import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from workflows import ProcessCartWorkflow
from activities import TxnProcessingActivities
from shared import ORDER_PROCESSING_TASK_QUEUE_NAME


## Starting the worker for processing realtime API calls
async def create_worker():
    client = await Client.connect("localhost:7233", namespace="default")
    activities = TxnProcessingActivities()
    worker = Worker(
        client, task_queue=ORDER_PROCESSING_TASK_QUEUE_NAME, workflows=[ProcessCartWorkflow], activities=[activities.check_balance_activity,activities.submit_order_activity, activities.process_payment_activity,activities.refund_payment_activity]
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(create_worker())