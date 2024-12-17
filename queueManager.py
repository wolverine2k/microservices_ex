from multiprocessing.managers import BaseManager

address = "127.0.0.1"
port = 50000
password = "secret"

class QueueManager(BaseManager):
    pass

def connect_to_manager():
    QueueManager.register('work_tasks_queue')
    QueueManager.register('done_task_queue')
    manager = QueueManager(address=(address, port), authkey=password.encode('utf-8'))
    manager.connect()
    return manager.work_tasks_queue(), manager.done_task_queue()