import subprocess
import time
import html
import sys
import psutil

port = "2010"

def mml_source_document(star_math_5: str) -> str:
    encoded = html.escape(star_math_5)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
<semantics>
<annotation encoding="StarMath 5.0">{encoded}</annotation>
</semantics>
</math>'''

def get_unoserver_memory(pid: int) -> int:
    try:
        process = psutil.Process(pid)
        return process.memory_info().rss // 1024
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return -1

def run_stress_test(input_content: str, port: str, unoserver_pid: int):    
    try:
        unoserver_process = psutil.Process(unoserver_pid)
        cmdline = " ".join(unoserver_process.cmdline())
        print(f"Monitoring unoserver process (PID: {unoserver_pid}): {cmdline}", file=sys.stderr)
    except psutil.NoSuchProcess:
        print(f"Error: No process found with PID {unoserver_pid}", file=sys.stderr)
        return
    except psutil.AccessDenied:
        print(f"Error: Access denied to process with PID {unoserver_pid}", file=sys.stderr)
        return
    
    i = 0
    while True:
        i = i + 1
        start_time = time.time()
        start_str = time.strftime('%H:%M:%S', time.localtime(start_time))
        mem_usage = get_unoserver_memory(unoserver_pid)
        print(f"[{i}] Starting conversion at {start_str} [Memory: {mem_usage} KB]", file=sys.stderr)

        try:
            result = subprocess.run(
                ["unoconvert", "--convert-to", "mml", "--port", port, "-", "-"],
                input=input_content.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            output = result.stdout.decode("utf-8")
            duration = time.time() - start_time
            mem_usage = get_unoserver_memory(unoserver_pid)

            if "α" in output and "≠" in output and "β" in output:
                status = "OK"
            else:
                status = "KO"

            print(f"[{i}] Conversion {status} in {duration} seconds [Memory: {mem_usage} KB]", file=sys.stderr)
            # TSV output (now includes memory usage)
            print(f"{i}\t{start_str}\t{status}\t{duration}\t{mem_usage}")

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            mem_usage = get_unoserver_memory(unoserver_pid)
            print(f"[{i}] Conversion FAILED in {duration} seconds [Memory: {mem_usage} KB]", file=sys.stderr)
            print(f"stderr: {e.stderr.decode('utf-8')}", file=sys.stderr)
            # TSV output with KO status (now includes memory usage)
            print(f"{i}\t{start_str}\tKO\t{duration}\t{mem_usage}")


if __name__ == "__main__":       
    unoserver_pid = int(sys.argv[1])
    run_stress_test(mml_source_document("%alpha <> %beta"), port, unoserver_pid)