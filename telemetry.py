import time

class PipelineTelemetry:
    """
    The Subject (Observable).
    Monitors queue sizes and notifies registered observers.
    """
    def __init__(self, raw_q, processed_q):
        self._raw_q = raw_q
        self._processed_q = processed_q
        self._observers = []
        self._current_stats = {"raw_fill": 0, "processed_fill": 0}

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self._current_stats)

    def poll_queues(self):
        """
        Calculates the percentage fill of each bounded queue.
        """
        # Note: qsize() is approximate but sufficient for telemetry
        raw_fill = (self._raw_q.qsize() / self._raw_q._maxsize) * 100
        proc_fill = (self._processed_q.qsize() / self._processed_q._maxsize) * 100
        
        self._current_stats = {
            "raw_fill": round(raw_fill, 2),
            "processed_fill": round(proc_fill, 2)
        }
        self.notify()
