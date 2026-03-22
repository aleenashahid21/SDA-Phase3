import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import collections

class DashboardObserver:
    """
    The Observer:
    Subscribes to Telemetry and renders the Live Graph.
    """
    def __init__(self, config, final_stream, telemetry_subject):
        self.config = config
        self.final_stream = final_stream
        self.telemetry = telemetry_subject
        
      
        self.telemetry.attach(self)
        
        #buffers for plotting
        self.max_points = 100
        self.times = collections.deque(maxlen=self.max_points)
        self.raw_values = collections.deque(maxlen=self.max_points)
        self.avg_values = collections.deque(maxlen=self.max_points)
        
        #telemetry storage
        self.latest_stats = {"raw_fill": 0, "processed_fill": 0}

    def update(self, stats):
        """Called by the Telemetry Subject (Observer Pattern)"""
        self.latest_stats = stats

    def _process_data(self):
        """Drains the final stream into local buffers for plotting."""
        try:
            while not self.final_stream.empty():
                packet = self.final_stream.get_nowait()
                if packet is None:
                    continue
                
                #use generic keys from config mapping
                self.times.append(packet.get("time_period", 0))
                self.raw_values.append(packet.get("metric_value", 0.0))
                self.avg_values.append(packet.get("computed_metric", 0.0))
        except Exception:
            pass

    def animate(self, i):
        """The Full Animation Loop: Updates data, sorts it, and renders."""
        self.telemetry.poll_queues()
        self._process_data()

        if not self.times or len(self.times) < 2:
            return

        plt.clf()
        
        #sorting data, fixes the scribble look from parallel processing)
        combined = sorted(zip(list(self.times), list(self.raw_values), list(self.avg_values)))
        sorted_times, sorted_raw, sorted_avg = zip(*combined)

        
        start_ts = sorted_times[0]
        relative_times = [t - start_ts for t in sorted_times]

       
        ax1 = plt.subplot(2, 1, 1)
        ax1.plot(relative_times, sorted_raw, label="Raw Sensor", color='#3498db', alpha=0.4)
        ax1.plot(relative_times, sorted_avg, label="Running Avg", color='#e74c3c', linewidth=2)
        ax1.set_title(f"Live Stream: {self.config['dataset_path']}")
        ax1.legend(loc="upper left")

        
        ax2 = plt.subplot(2, 1, 2)
        raw_f = self.latest_stats.get("raw_fill", 0)
        proc_f = self.latest_stats.get("processed_fill", 0)
        
        queues = ['Input Queue', 'Core Queue']
        fills = [raw_f, proc_f]
        colors = ['#2ecc71' if f < 50 else '#f1c40f' if f < 80 else '#e74c3c' for f in fills]

        ax2.barh(queues, fills, color=colors)
        ax2.set_xlim(0, 100)
        ax2.set_title("System Backpressure Telemetry (%)")
        
        plt.tight_layout()

    def render_loop(self):
        """Start the Matplotlib window."""
        fig = plt.figure(figsize=(10, 8))
        
        ani = FuncAnimation(fig, self.animate, interval=100, cache_frame_data=False)
        plt.show()
