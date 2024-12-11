from multiprocessing.managers import BaseManager
import time

# Define a custom Manager to connect to the shared dictionary and queue
class CallbackManager(BaseManager):
    pass

# Define a function to be called as a callback with parameters
def client2_callback1(param1, param2):
    print(f"Client1 callback1 executed with parameters: param1={param1}, param2={param2}")

# Define a function to be called as a callback with parameters
def client2_callback2(param1, param2, param3, param4):
    print(f"Client1 callback2 executed with parameters: param1={param1}, param2={param2}, param3={param3}, param4={param4}")

if __name__ == "__main__":
    # Register the shared dictionary and queue with the Manager
    CallbackManager.register("callback_dict")
    CallbackManager.register("notification_queue")

    # Connect to the server (same system, so localhost is used)
    manager = CallbackManager(address=("localhost", 50000), authkey=b"secret")
    manager.connect()

    # Get access to the shared dictionary and notification queue
    callback_dict = manager.callback_dict()
    notification_queue = manager.notification_queue()

    # Register the callback by name with parameters
    print("Registering client2 callback1.")
    callback_dict.update({
        "client2_callback1": {
            "active": True,
            "params": (22, "example2")  # Example parameters
        }
    })

    # Register the callback by name with parameters
    print("Registering client2 callback2.")
    callback_dict.update({
        "client2_callback2": {
            "active": True,
            "params": (22, "example2", "param3-222", 200)  # Example parameters
        }
    })

    # Start listening for notifications
    print("Listening for callback notifications...")
    try:
        while True:
            # Check for notifications from the server
            if not notification_queue.empty():
                message = notification_queue.get()
                callback_name = message.get("name")
                params = message.get("params", ())

                if callback_name == "client2_callback1":
                    client2_callback1(*params)  # Execute the callback with parameters
                elif callback_name == "client2_callback2":
                    client2_callback2(*params)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Shutting down client.")
