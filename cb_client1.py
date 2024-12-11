from multiprocessing.managers import BaseManager
import time

# Define a custom Manager to connect to the shared dictionary and queue
class CallbackManager(BaseManager):
    pass

# Define a function to be called as a callback
def client_callback():
    print("Client callback executed in client context.")

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

    # Register the callback by name
    print("Registering client callback.")
    callback_dict.update({"client_callback": {"active": True}})

    # Start listening for notifications
    print("Listening for callback notifications...")
    try:
        while True:
            # Check for notifications from the server
            if not notification_queue.empty():
                callback_name = notification_queue.get()
                if callback_name == "client_callback":
                    client_callback()  # Execute the callback in the client context
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Shutting down client.")
