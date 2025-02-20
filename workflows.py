from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from shared import ASYNC_ORDER_PROCESSING_TASK_QUEUE_NAME
from temporalio.workflow import ParentClosePolicy
import asyncio

## Need read more about what imports_passed_through are; most probably looks related to the pyenv libs; had an issue using uuid here
with workflow.unsafe.imports_passed_through():
    from activities import TxnProcessingActivities
    from shared import CartInfo
    import uuid

## Workflow definition for Aysnc post processing
@workflow.defn
class PostProcessCartWorkflow:
    @workflow.run
    async def run_wf(self, cart: CartInfo) -> str:
        queue_indefinite_retry_policy = RetryPolicy(
            maximum_attempts=0,
            maximum_interval=timedelta(seconds=5),
            non_retryable_error_types=[],
        )
        # check customer_service
        # Any exception on this service (be it 404 customer not found or some other system/api error) keep retrying
        customer_service_output = await workflow.execute_activity_method(
            TxnProcessingActivities.customer_service_activity,
            cart,
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=queue_indefinite_retry_policy,
        )
        #send_email_receipt; keep retying if there are issues with the email service
        send_email_receipt_output = await workflow.execute_activity_method(
            TxnProcessingActivities.send_email_receipt_activity,
            customer_service_output,
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=queue_indefinite_retry_policy,
        )
        #send_email_offer after 30 days; keep retying if there are issues with the email service
        await asyncio.sleep(30)
        send_email_offer_output = await workflow.execute_activity_method(
            TxnProcessingActivities.send_email_offer_activity,
            customer_service_output,
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=queue_indefinite_retry_policy,
        )

        return send_email_receipt_output + " | " + send_email_offer_output


## Workflow definition for Sync API
@workflow.defn
class ProcessCartWorkflow:
    @workflow.run
    async def run_wf(self, cart: CartInfo) -> str:
        api_default_retry_policy = RetryPolicy(
            maximum_attempts=2,
            maximum_interval=timedelta(seconds=1),
            non_retryable_error_types=["NotEnoughBalanceNoRetry","InvalidCardErrorNoRetry"],
        )

        #check balance; dont retry if expected custom exception; use maximum_attempts when other exceptions
        check_balance_output = await workflow.execute_activity_method(
            TxnProcessingActivities.check_balance_activity,
            cart,
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=api_default_retry_policy,
        )
        #process payment; dont retry if expected custom exception; use maximum_attempts when other exceptions
        process_payment_output = await workflow.execute_activity_method(
                TxnProcessingActivities.process_payment_activity,
                cart,
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=api_default_retry_policy,
        )

        try:
            submit_order_output = await workflow.execute_activity_method(
                TxnProcessingActivities.submit_order_activity,
                cart,
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=api_default_retry_policy,
            )
        ## I have mocked a case to come to the refund flow just to show the orchestrate behavior
        except Exception:
            refund_payment_output = await workflow.execute_activity_method(
                TxnProcessingActivities.refund_payment_activity,
                process_payment_output,
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=api_default_retry_policy,
            )
            return refund_payment_output

        # Calling child worklflow for Async post processing; using parent policy ABANDON so that parent workflow completes as soon as post processing
        # is handed over to the post processing Task Queue; this will only wait for handle of the child workflow
        submit_post_processing_handle = await workflow.start_child_workflow(
            PostProcessCartWorkflow.run_wf,
            cart,
            task_queue=ASYNC_ORDER_PROCESSING_TASK_QUEUE_NAME,
            parent_close_policy=ParentClosePolicy.ABANDON
        )
        return check_balance_output + " | " + process_payment_output + " | " + submit_order_output + " | " + str(submit_post_processing_handle)
