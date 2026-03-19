import json
import queue
import threading
from telemetry import TelemetryStream
from core_module import CoreModule
from output_module import OutputModule

def run_core(core, raw_queue, processed_queue):
    while True:
        core.run(raw_queue, processed_queue)

def run_output(config, processed_queue):
    while True:
        OutputModule.run(config, processed_queue)

def main():
    # Load configuration
    with open("config.json", "r") as f:
        config = json.load(f)

    # Queues
    raw_queue = queue.Queue(maxsize=config["pipeline_dynamics"]["stream_queue_max_size"])
    processed_queue = queue.Queue()

    # Initialize modules
    telemetry = TelemetryStream(config, raw_queue)
    core = CoreModule(config)

    # Threads for Core and Output
    core_thread = threading.Thread(target=run_core, args=(core, raw_queue, processed_queue), daemon=True)
    output_thread = threading.Thread(target=run_output, args=(config, processed_queue), daemon=True)

    core_thread.start()
    output_thread.start()

    # Start telemetry stream (main thread)
    try:
        telemetry.stream()
    except KeyboardInterrupt:
        print("\nPipeline stopped by user.")

if __name__ == "__main__":
    main()