import subprocess
import threading
import queue
import keyboard
import sys
import time


def enqueue_output(out, q):
    try:
        for line in iter(out.readline, ''):
            q.put(line)
    except Exception as e:
        q.put(f"Error reading output: {e}")
    out.close()


def stream_output(name, output_queue, error_queue, display_queue, stop_event, log_file):
    with open(log_file, 'a') as f:
        while not stop_event.is_set() or not output_queue.empty() or not error_queue.empty():
            try:
                output = output_queue.get_nowait()
                if output:
                    display_queue.put(f"[{name}] {output.strip()}")
                    f.write(f"[{name}] {output.strip()}\n")
            except queue.Empty:
                pass

            try:
                error = error_queue.get_nowait()
                if error:
                    display_queue.put(f"[{name} System] {error.strip()}")
                    f.write(f"[{name} System] {error.strip()}\n")
            except queue.Empty:
                pass


def execute_script(script, name, display_queue, stop_event, log_file):
    try:
        process = subprocess.Popen(
            ['python', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )

        output_queue = queue.Queue()
        error_queue = queue.Queue()

        stdout_thread = threading.Thread(target=enqueue_output, args=(process.stdout, output_queue))
        stderr_thread = threading.Thread(target=enqueue_output, args=(process.stderr, error_queue))
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()

        stream_output(name, output_queue, error_queue, display_queue, stop_event, log_file)

        stdout_thread.join()
        stderr_thread.join()
        process.wait()
    except Exception as e:
        display_queue.put(f"Failed to execute {script}: {e}")


def main():
    display_queue_1 = queue.Queue()
    display_queue_2 = queue.Queue()
    stop_event_1 = threading.Event()
    stop_event_2 = threading.Event()

    log_file_1 = "generate_server_log.txt"
    log_file_2 = "server_log.txt"

    scripts = [
        (
            "C:\\Users\\whps9\\ccoliu.github.io\\Servers\\generateServerFinalVer.py",
            "Generate Server",
            display_queue_1,
            stop_event_1,
            log_file_1,
        ),
        (
            "C:\\Users\\whps9\\ccoliu.github.io\\Servers\\restServerFinalVer.py",
            "Server",
            display_queue_2,
            stop_event_2,
            log_file_2,
        ),
    ]

    threads = []
    for script, name, display_queue, stop_event, log_file in scripts:
        thread = threading.Thread(
            target=execute_script, args=(script, name, display_queue, stop_event, log_file)
        )
        threads.append(thread)
        thread.start()

    current_display_queue = display_queue_1
    output_history = {1: [], 2: []}

    def show_output():
        while True:
            while not current_display_queue.empty():
                line = current_display_queue.get()
                if current_display_queue == display_queue_1:
                    output_history[1].append(line)
                else:
                    output_history[2].append(line)
                print(line)
            if stop_event_1.is_set() and stop_event_2.is_set():
                break
            time.sleep(0.1)  # To prevent high CPU usage

    def display_history(queue_number):
        print("\n" + "-" * 20 + f" Displaying {queue_number} output " + "-" * 20 + "\n")
        for line in output_history[queue_number]:
            print(line)

    def switch_to_1():
        nonlocal current_display_queue
        current_display_queue = display_queue_1
        display_history(1)

    def switch_to_2():
        nonlocal current_display_queue
        current_display_queue = display_queue_2
        display_history(2)

    def quit_program():
        stop_event_1.set()
        stop_event_2.set()
        sys.exit()

    keyboard.add_hotkey('k', switch_to_1)
    keyboard.add_hotkey('l', switch_to_2)
    keyboard.add_hotkey('q', quit_program)

    try:
        show_output()
    except KeyboardInterrupt:
        stop_event_1.set()
        stop_event_2.set()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
