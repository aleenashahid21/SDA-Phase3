from queue import Queue

# Shared queues for pipeline and dashboard
raw_queue = Queue(maxsize=50)        # adjust maxsize if needed
processed_queue = Queue(maxsize=50)
