import multiprocessing
import json
from module.input_module import InputWorker
from module.core_module import ComputeWorker, AggregatorWorker
from module.telemetry import PipelineTelemetry
from module.output_module import DashboardObserver

def main():
    with open("config.json", 'r') as f:
        config = json.load(f)
    
    dyn = config["pipeline_dynamics"]
    max_q = dyn["stream_queue_max_size"]

    #injecting Concrete Multi-processing objects into the IStream protocol
    raw_q = multiprocessing.Queue(maxsize=max_q)
    proc_q = multiprocessing.Queue(maxsize=max_q)
    out_q = multiprocessing.Queue()

    procs = []
    #input worker injected with path, delay, schema, and IStream
    procs.append(multiprocessing.Process(target=InputWorker.run, 
        args=(config["dataset_path"], dyn["input_delay_seconds"], config["schema_mapping"]["columns"], raw_q)))
    
    #scatter pool injected with settings and IStreams
    for _ in range(dyn["core_parallelism"]):
        procs.append(multiprocessing.Process(target=ComputeWorker.run, 
            args=(config["processing"]["stateless_tasks"], raw_q, proc_q)))
    
    #gather node injected with window and IStreams
    procs.append(multiprocessing.Process(target=AggregatorWorker.run, 
        args=(config["processing"]["stateful_tasks"]["running_average_window_size"], proc_q, out_q)))

    telemetry = PipelineTelemetry({"Input Q": raw_q, "Core Q": proc_q}, max_q)
    dashboard = DashboardObserver(config, out_q, telemetry)

    for p in procs: p.start()
    try:
        dashboard.render_loop()
    finally:
        for p in procs: p.terminate()

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)
    main()
