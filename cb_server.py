from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
import time

#Define the trigger callback process
def trigger_callbacks(manager_dict, client_queues, shared_queue):
    """Only trigger callbacks and notify the respective client queues on interest"""
    while True:
        if not client_queues:
            time.sleep(5)
            continue
        
        while client_queues:
            trigger = client_queues.popitem()
            print(trigger[0])
            for name, callback_info in list(manager_dict.items()):
                for client_callback, cb_info in list(callback_info.items()):
                    if cb_info["interest"] == trigger[0]:
                        shared_queue.put({"name": client_callback, "params": cb_info.get("params", ())})
            time.sleep(0.5)
        time.sleep(2)

# Define the callback registry process
def callback_registry(manager_dict, client_queues, shared_queue):
    """Monitor callbacks and notify the respective client queues."""
    while True:
        # We will see if there is trigger and only then execute
        '''
        for name, callback_info in list(manager_dict.items()):
            if name in client_queues:
                for client_callback, cb_info in list(callback_info.items()):
                    if cb_info["active"]:
                        shared_queue.put({"name": client_callback, "params": cb_info.get("params", ())})
                        cb_info["active"] = False
        '''
        time.sleep(1)

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
    #registry_process.start()

    # Start the trigger process
    trigger_process = Process(target=trigger_callbacks, args=(callback_dict, client_queues, shared_queue))
    trigger_process.start()

    print("Callback registry server is running on localhost:50000.")
    
    try:
        while True:
            time.sleep(1)  # Keep the server running
    except KeyboardInterrupt:
        print("Shutting down callback server.")
        registry_process.terminate()
        trigger_process.terminate()
        manager_server.shutdown()
