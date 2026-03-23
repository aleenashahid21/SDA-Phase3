from typing import Dict, List
from contracts import IStream, IObserver, ISubject

class PipelineTelemetry(ISubject):
    def __init__(self, streams: Dict[str, IStream], max_size: int):
        self._streams = streams
        self._max_size = max_size
        self._observers: List[IObserver] = []

    def attach(self, observer: IObserver):
        self._observers.append(observer)

    def notify(self, stats: Dict[str, float]):
        for obs in self._observers:
            obs.update(stats)

    def poll(self):
        stats = {name: (s.qsize() / self._max_size) * 100 for name, s in self._streams.items()}
        self.notify(stats)
