import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from workflows import PostProcessCartWorkflow
from activities import TxnProcessingActivities
from shared import ASYNC_ORDER_PROCESSING_TASK_QUEUE_NAME

## Starting the worker for Aysnc post processing
async def create_worker():
    client = await Client.connect("localhost:7233", namespace="default")
    activities = TxnProcessingActivities()
    worker = Worker(
        client, task_queue=ASYNC_ORDER_PROCESSING_TASK_QUEUE_NAME, workflows=[PostProcessCartWorkflow], activities=[activities.customer_service_activity,activities.send_email_receipt_activity,activities.send_email_offer_activity]
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(create_worker())