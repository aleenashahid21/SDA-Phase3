from collections import deque


def run_aggregator(config, processed_queue, final_queue):
    print("Aggregator started.")

    window_size = config["processing"]["stateful_tasks"]["running_average_window_size"]
    window = deque(maxlen=window_size)

    while True:
        packet = processed_queue.get()

        if packet is None:
            final_queue.put(None)
            break

        window.append(packet["metric_value"])

        avg = sum(window) / len(window)

        packet["computed_metric"] = avg

        print("Aggregator sending:", packet)

        final_queue.put(packet)
