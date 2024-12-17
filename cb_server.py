from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
import time

# Define the callback registry process
def callback_registry(manager_dict, client_queues, shared_queue):
    """Monitor callbacks and notify the respective client queues."""
    while True:
        for name, callback_info in list(manager_dict.items()):
            if name in client_queues:
                for client_callback, cb_info in list(callback_info.items()):
                    if cb_info["active"]:
                        shared_queue.put({"name": client_callback, "params": cb_info.get("params", ())})
                        cb_info["active"] = False
            time.sleep(1)
        time.sleep(1)
'''                    
            print (callback_info)
            if callback_info["active"]:
                print(f"Notifying client to execute callback: {name}")
                if name in client_queues:
                    client_queue = client_queues[name]
                    client_queue.put({"name": name, "params": callback_info.get("params", ())})
                callback_info["active"] = False
        time.sleep(1)
'''

# Define a custom manager class to share the dictionary and queues remotely
class CallbackManager(BaseManager):
    pass

if __name__ == "__main__":
    # Create a Manager to handle shared state
    manager = Manager()
    callback_dict = manager.dict()  # Shared dictionary for callback registration
    client_queues = manager.dict()  # Shared dictionary for client notification queues
    shared_queue = manager.Queue()

    # Register shared structures with the manager
    CallbackManager.register("callback_dict", callable=lambda: callback_dict)
    CallbackManager.register("client_queues", callable=lambda: client_queues)
    CallbackManager.register("shared_queue", callable=lambda: shared_queue)  # Register Queue

    # Start the manager server on localhost:50000
    password = "secret"
    manager_server = CallbackManager(address=("localhost", 50000), authkey=password.encode('utf-8'))
    manager_server.start()

    # Start the registry process
    registry_process = Process(target=callback_registry, args=(callback_dict, client_queues, shared_queue))
    registry_process.start()

    print("Callback registry server is running on localhost:50000.")
    
    try:
        while True:
            time.sleep(1)  # Keep the server running
    except KeyboardInterrupt:
        print("Shutting down callback server.")
        registry_process.terminate()
        manager_server.shutdown()
