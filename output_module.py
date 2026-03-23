import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import collections
from contracts import IObserver

class DashboardObserver(IObserver):
    def __init__(self, config, final_stream, telemetry_subject):
        self.config = config
        self.final_stream = final_stream
        self.telemetry = telemetry_subject
        self.telemetry.attach(self)
        
        # prevents memory overflow
        self.max_points = 100
        self.data_buffers = collections.defaultdict(lambda: collections.deque(maxlen=self.max_points))
        self.latest_stats = {}

    def update(self, stats: dict):
        self.latest_stats = stats

    def _process_data(self):
        """Drains the stream but limits processing per frame to prevent GUI lockup."""
        count = 0
        try:
            # only process up to 50 packets per animation frame
            while not self.final_stream.empty() and count < 50:
                packet = self.final_stream.get_nowait()
                if packet:
                    for k, v in packet.items():
                        self.data_buffers[k].append(v)
                count += 1
        except:
            pass

    def animate(self, i, ax1, ax2):
        self.telemetry.poll()
        self._process_data()
        
        #check if we have data to plot
        x_key = "time_period"
        if len(self.data_buffers[x_key]) < 2:
            return

        #clear axes instead of the whole figure
        ax1.cla()
        ax2.cla()

        #sort and Plot Data (Fixes the zigzag 'scribble' look)
        y_keys = [chart["y_axis"] for chart in self.config["visualizations"]["data_charts"]]
        
        # zip, sort by time, and Plot
        combined = sorted(zip(list(self.data_buffers[x_key]), 
                             *[list(self.data_buffers[k]) for k in y_keys]))
        
        if combined:
            unzipped = list(zip(*combined))
            times = unzipped[0]
            for idx, y_key in enumerate(y_keys):
                ax1.plot(times, unzipped[idx+1], label=y_key)

        ax1.set_title("Real-Time Data Pipeline")
        ax1.legend(loc="upper left")

        #telemetry Bars
        if self.latest_stats:
            names = list(self.latest_stats.keys())
            vals = list(self.latest_stats.values())
            colors = ['#2ecc71' if v < 50 else '#f1c40f' if v < 80 else '#e74c3c' for v in vals]
            
            bars = ax2.barh(names, vals, color=colors)
            ax2.set_xlim(0, 100)
            ax2.set_title("System Backpressure (%)")
            
            for bar in bars:
                w = bar.get_width()
                ax2.text(w + 1, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', va='center')

    def render_loop(self):
        #reduce size to saves memory 
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        plt.tight_layout()
        
        #pass axes to animate to avoid repeated figure creation
        ani = FuncAnimation(fig, self.animate, fargs=(ax1, ax2), interval=200, cache_frame_data=False)
        plt.show()
