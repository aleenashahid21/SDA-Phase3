import json
import multiprocessing
from module.input_module import InputWorker
from module.core_module import ComputeWorker, AggregatorWorker
from module.telemetry import PipelineTelemetry
from module.output_module import DashboardObserver

def main():
    # 1. Load configuration
    with open("config.json", 'r') as f:
        config = json.load(f)
    
    dyn = config["pipeline_dynamics"]

    raw_stream = multiprocessing.Queue(maxsize=dyn["stream_queue_max_size"])
    
    processed_stream = multiprocessing.Queue(maxsize=dyn["stream_queue_max_size"])
    
    final_output_stream = multiprocessing.Queue()

    telemetry_subject = PipelineTelemetry(raw_stream, processed_stream)

    p_input = multiprocessing.Process(target=InputWorker.run, args=(config, raw_stream))

    p_compute = [
        multiprocessing.Process(target=ComputeWorker.run, args=(config, raw_stream, processed_stream))
        for _ in range(dyn["core_parallelism"])
    ]

    p_aggregator = multiprocessing.Process(target=AggregatorWorker.run, args=(config, processed_stream, final_output_stream))

    dashboard = DashboardObserver(config, final_output_stream, telemetry_subject)

    p_input.start()
    for p in p_compute: p.start()
    p_aggregator.start()

    try:
        dashboard.render_loop()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        p_input.terminate()
        p_aggregator.terminate()
        for p in p_compute: p.terminate()

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)
    main()
