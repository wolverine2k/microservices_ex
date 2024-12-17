from multiprocessing.managers import BaseManager
from multiprocessing import Queue
import time

# Define a custom Manager to connect to the shared dictionary and queue
class CallbackManager(BaseManager):
    pass

# Define a function to be called as a callback with parameters
def client1_callback1(param1, param2):
    print(f"Client1 callback1 executed with parameters: param1={param1}, param2={param2}")

# Define a function to be called as a callback with parameters
def client1_callback2(param1, param2, param3, param4):
    print(f"Client1 callback2 executed with parameters: param1={param1}, param2={param2}, param3={param3}, param4={param4}")

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
    client_queue_name = "client1"  # This name maps to the cleint
    client_queues.update({client_queue_name:client_queue_name})

    # Register the callback by name with parameters
    print("Registering client1 callback1.")
    callback_dict.update({
        client_queue_name:{
            "client1_callback1": {
                "active": True,
                "params": (11, "example1")  # Example parameters
            },
            "client1_callback2": {
                "active": True,
                "params": (11, "example1", "param3-111", 100)  # Example parameters
            }
        }
    })

    # Start listening for notifications
    print("Listening for callback notifications...")
    try:
        while True:
            # Check for notifications from the server
            if not notification_queue.empty():
                message = notification_queue.get()
                callback_client_name = message.get("name")
                params = message.get("params", ())

                if callback_client_name == "client1_callback1":
                    client1_callback1(*params)  # Execute the callback with parameters
                elif callback_client_name == "client1_callback2":
                    client1_callback2(*params)
                else:
                    notification_queue.put(message)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Shutting down client.")
