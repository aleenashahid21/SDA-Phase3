import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
from queues import raw_queue, processed_queue

def start_dashboard():
    sns.set(style="darkgrid")

    sensor_times, sensor_values, running_avgs = [], [], []
    MAX_POINTS = 200

    fig, (ax_queue, ax_values, ax_avg) = plt.subplots(3, 1, figsize=(12, 10))
    line_values, = ax_values.plot([], [], label="Sensor Values", color="blue")
    line_avg, = ax_avg.plot([], [], label="Running Average", color="orange")

    def update(frame):
        # Queue Monitoring
        raw_size = raw_queue.qsize()
        processed_size = processed_queue.qsize()
        ax_queue.clear()
        ax_queue.bar(["Raw Queue", "Processed Queue"], [raw_size, processed_size],
                     color=["green" if raw_size < 25 else "orange" if raw_size < 40 else "red",
                            "green" if processed_size < 25 else "orange" if processed_size < 40 else "red"])
        ax_queue.set_ylim(0, 50)
        ax_queue.set_title("Queue Status")

        # Consume only a few packets per frame
        for _ in range(min(3, processed_queue.qsize())):
            packet = processed_queue.get()
            sensor_times.append(packet["time_period"])
            sensor_values.append(packet["metric_value"])
            running_avgs.append(packet.get("running_avg", packet["metric_value"]))

        # Rolling window
        sensor_times[:] = sensor_times[-MAX_POINTS:]
        sensor_values[:] = sensor_values[-MAX_POINTS:]
        running_avgs[:] = running_avgs[-MAX_POINTS:]

        # Update lines
        line_values.set_data(sensor_times, sensor_values)
        line_avg.set_data(sensor_times, running_avgs)

        ax_values.relim(); ax_values.autoscale_view()
        ax_avg.relim(); ax_avg.autoscale_view()

        ax_values.set_title("LIVE Sensor Values")
        ax_values.legend()
        ax_avg.set_title("Live Sensor Running Average")
        ax_avg.legend()

        # Debug overlay
        ax_values.text(0.01, 0.95, f"Packets plotted: {len(sensor_values)}",
                       transform=ax_values.transAxes, fontsize=9, color="gray")

        return line_values, line_avg

    ani = animation.FuncAnimation(fig, update, interval=2000, blit=False, cache_frame_data=False)
    plt.tight_layout()
    plt.show()
