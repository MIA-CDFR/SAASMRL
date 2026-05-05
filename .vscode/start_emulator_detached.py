import os
import subprocess
import sys
import time


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: start_emulator_detached.py <emulator_path> <log_path> <args...>", file=sys.stderr)
        return 2

    emulator_path = sys.argv[1]
    log_path = sys.argv[2]
    emulator_args = sys.argv[3:]

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    with open(log_path, "ab", buffering=0) as log_file:
        process = subprocess.Popen(
            [emulator_path, *emulator_args],
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
        )

        time.sleep(1)
        return_code = process.poll()
        if return_code is not None:
            print(f"Emulator exited immediately with code {return_code}. Check {log_path}.", file=sys.stderr)
            return return_code

        print(process.pid)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())