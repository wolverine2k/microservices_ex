from multiprocessing.managers import BaseManager
from multiprocessing import Queue
import time

# Define a custom Manager to connect to the shared dictionary and queue
class CallbackManager(BaseManager):
    pass

# Define a function to be called as a callback with parameters
def client2_callback1(param1, param2, client_queues):
    print(f"Client2 callback1 executed with parameters: param1={param1}, param2={param2}")
    client_queues.update({"2000":client_queue_name})

# Define a function to be called as a callback with parameters
def client2_callback2(param1, param2, param3, param4,client_queues):
    print(f"Client2 callback2 executed with parameters: param1={param1}, param2={param2}, param3={param3}, param4={param4}")
    client_queues.update({"2001":client_queue_name})

if __name__ == "__main__":
    # Register the shared dictionary and queue with the Manager
    CallbackManager.register("callback_dict")
    CallbackManager.register("client_queues")
    CallbackManager.register("shared_queue")  # Register Queue for creating manager-provided queues

    # Connect to the server (same system, so localhost is used)
    password = "secret"
    manager = CallbackManager(address=("localhost", 50000), authkey=password.encode('utf-8'))
    manager.connect()

    # Get access to the shared dictionary and notification queue
    callback_dict = manager.callback_dict()
    client_queues = manager.client_queues()

    # Create a manager-provided notification queue
    notification_queue = manager.shared_queue()

    # Register the client queue with the server
    client_queue_name = "client2"  # This name maps to the cleint
    #client_queues.update({client_queue_name:client_queue_name})

    # Register the callback by name with parameters
    print("Registering client2 callbacks.")
    callback_dict.update({
        client_queue_name:{
            "client2_callback1": {
                "active": True,
                "params": (22, "example2"),  # Example parameters
                "interest": "1000"
            },
            "client2_callback2": {
                "active": True,
                "params": (22, "example2", "param3-222", 200),  # Example parameters
                "interest": "1001"
            }
        }
    })

    client_queues.update({"2000":client_queue_name})
    client_queues.update({"2001":client_queue_name})

    # Start listening for notifications
    print("Listening for callback notifications...")
    try:
        while True:
            # Check for notifications from the server
            if not notification_queue.empty():
                message = notification_queue.get()
                callback_client_name = message.get("name")
                params = message.get("params", ())

                if callback_client_name == "client2_callback1":
                    client2_callback1(*params, client_queues)  # Execute the callback with parameters
                elif callback_client_name == "client2_callback2":
                    client2_callback2(*params, client_queues)
                else:
                    notification_queue.put(message)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Shutting down client.")
