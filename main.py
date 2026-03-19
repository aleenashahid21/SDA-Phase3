import json
import threading
import time
from telemetry import TelemetryStream
from core_module import CoreModule
from output_module import OutputModule
from queues import raw_queue, processed_queue
import dashboard


def run_core(core, raw_queue, processed_queue):
    core.run(raw_queue, processed_queue)


def run_output(config, processed_queue):
    OutputModule.run(config, processed_queue)


def run_telemetry(telemetry):
    telemetry.stream()


def main():
    with open("config.json", "r") as f:
        config = json.load(f)

    telemetry = TelemetryStream(config, raw_queue)
    core = CoreModule(config)

    threads = [
        threading.Thread(target=run_core, args=(core, raw_queue, processed_queue),
                         daemon=True, name="CoreWorker"),
        threading.Thread(target=run_output, args=(config, processed_queue),
                         daemon=True, name="OutputWorker"),
        threading.Thread(target=run_telemetry, args=(telemetry,),
                         daemon=True, name="TelemetryWorker"),
    ]

    for t in threads:
        t.start()

    time.sleep(0.5)
    print("✅ All worker threads started:", [t.name for t in threads])

    dashboard.start_dashboard()
    print("\nDashboard closed — pipeline finished.\n")


if __name__ == "__main__":
    main()
