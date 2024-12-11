from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
import time

# Define the callback registry process
def callback_registry(manager_dict, notification_queue):
    """A process that monitors callbacks and notifies clients."""
    while True:
        for name, callback_info in list(manager_dict.items()):
            if callback_info["active"]:
                print(f"Notifying client to execute callback: {name}")
                # Send the callback name and parameters to the notification queue
                notification_queue.put({"name": name, "params": callback_info.get("params", ())})
                callback_info["active"] = False
        time.sleep(10)

# Define a custom manager class to share the dictionary and queue remotely
class CallbackManager(BaseManager):
    pass

if __name__ == "__main__":
    # Create a Manager to handle shared state
    manager = Manager()
    callback_dict = manager.dict()

    # Create a notification queue for callback execution
    notification_queue = manager.Queue()

    # Register the shared dictionary and queue with the manager
    CallbackManager.register("callback_dict", callable=lambda: callback_dict)
    CallbackManager.register("notification_queue", callable=lambda: notification_queue)

    # Start the manager server on localhost:50000
    manager_server = CallbackManager(address=("localhost", 50000), authkey=b"secret")
    manager_server.start()

    # Start the registry process
    registry_process = Process(target=callback_registry, args=(callback_dict, notification_queue))
    registry_process.start()

    print("Callback registry server is running on localhost:50000.")
    
    try:
        while True:
            time.sleep(1)  # Keep the server running
    except KeyboardInterrupt:
        print("Shutting down callback server.")
        registry_process.terminate()
        manager_server.shutdown()
