import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import sys
import requests
import json
import traceback

import asyncio
import traceback
import uuid
from workflows import ProcessCartWorkflow
from temporalio.client import Client, WorkflowFailureError
from temporalio.exceptions import ApplicationError
from shared import ORDER_PROCESSING_TASK_QUEUE_NAME, CartInfo

## My attepmt to submit the card payload via postman instead of running the run_workflow
## More work needs to be done here because the exceptions returned from the workflow client are not the actual application exceptions
## Need to catch application exceptions and convert those into the valid HTTP codes and response message
## This is working for happy path but not for exception scenarios

class S(BaseHTTPRequestHandler):
    async def submit_to_wf(self, cart:CartInfo) -> str:
        # Create client connected to server at the given address
        client = await Client.connect("localhost:7233")
        try:
            result = await client.execute_workflow(
                ProcessCartWorkflow.run_wf,
                cart,
                id=cart.cart_id + "-" + cart.cust_id,
                task_queue=ORDER_PROCESSING_TASK_QUEUE_NAME,
            )
            return result
        except WorkflowFailureError:
            print("Got expected exception: ", traceback.format_exc())


    def handle_post(self):
        try:
            content_length = self.headers['Content-Length']
            content_length = 0 if (content_length is None) else int(content_length)
            msg_body_bytes = self.rfile.read(content_length)
            msg_body_bytes_json_dict = json.loads(msg_body_bytes)
            cart = CartInfo(**msg_body_bytes_json_dict)
            time.sleep(1)
            post_result = asyncio.run(self.submit_to_wf(cart))
            if post_result != None:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write((post_result).encode('utf-8'))
            else:
                self.send_error(500, "Some Workflow Error")
        except WorkflowFailureError:
            self.send_error(500, "Some WorkflowFailureError Error")
        except ApplicationError:
            self.send_error(404, "NotEnoughBalance Error")
        except Exception as e:
            self.send_error(500, "Some Unhandled Server Error")
# traceback.format_exc()
### Below is to handle the post method call on the http server
    def do_POST(self):
        self.handle_post()

###Below is for starting up the HTTP server
def run(address, port, server_class=HTTPServer, handler_class=S):
    logging.basicConfig(level=logging.INFO)
    server_address = (address, port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage:\n" + sys.argv[0] + " [address] [port]")
        sys.exit(1)

    run(sys.argv[1], int(sys.argv[2]))