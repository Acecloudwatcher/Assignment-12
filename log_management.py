import time
import random
from threading import Thread, current_thread, Condition

class LogBuffer:
    def __init__(self):
        self.current_log = None
        self.is_empty = True
        self.condition = Condition()

    def write_log(self, log_msg):
        # TODO: Acquire the condition lock, wait while the buffer is NOT empty
        # (previous log not yet archived), then write the new log and notify
        # the archiver.
        with self.condition:
            # Wait until the buffer is empty (archiver has consumed the last log)
            while not self.is_empty:
                print("[Generator] Buffer is full — waiting for archiver...")
                self.condition.wait()

            # Write the log entry into the shared buffer
            self.current_log = log_msg
            self.is_empty = False
            print(f"[Generator] Written log  --> {self.current_log}")

            # Notify the archiver that a new log is ready
            self.condition.notify()

    def archive_log(self):
        # TODO: Acquire the condition lock, wait while the buffer IS empty
        # (no log written yet), then read and clear the log and notify
        # the generator.
        with self.condition:
            # Wait until the buffer has a log ready to be archived
            while self.is_empty:
                print("[Archiver]  Buffer is empty — waiting for generator...")
                self.condition.wait()

            # Read and process (archive) the log entry
            log_to_archive = self.current_log
            print(f"[Archiver]  Archiving log --> {log_to_archive}")
            time.sleep(random.uniform(0.1, 0.5))  # Simulate archival work

            # Clear the buffer
            self.current_log = None
            self.is_empty = True
            print(f"[Archiver]  Archived log  --> {log_to_archive}  [DONE]")

            # Notify the generator that the buffer is free
            self.condition.notify()


class LogGenerator(Thread):
    # TODO: Implement the LogGenerator thread.
    # It generates LOG_COUNT log messages and writes each to the shared buffer,
    # simulating a real service producing log entries over time.

    def __init__(self, buffer, log_count):
        super().__init__(name="LogGenerator")
        self.buffer = buffer
        self.log_count = log_count

    def run(self):
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"]
        services   = ["auth-service", "db-service", "api-gateway", "scheduler", "cache"]

        print(f"\n{'='*60}")
        print(f"  {self.name} started — will produce {self.log_count} logs")
        print(f"{'='*60}\n")

        for i in range(1, self.log_count + 1):
            level   = random.choice(log_levels)
            service = random.choice(services)
            msg = f"[{level}] ({service}) Log entry #{i}"

            time.sleep(random.uniform(0.1, 0.4))  # Simulate log generation delay
            self.buffer.write_log(msg)

        print(f"\n[Generator] All {self.log_count} logs produced. Generator exiting.")


class LogArchiver(Thread):
    # TODO: Implement the LogArchiver thread.
    # It archives LOG_COUNT log entries from the shared buffer,
    # simulating the disk-space-saving archival process.

    def __init__(self, buffer, log_count):
        super().__init__(name="LogArchiver")
        self.buffer = buffer
        self.log_count = log_count

    def run(self):
        print(f"\n{'='*60}")
        print(f"  {self.name} started — will archive {self.log_count} logs")
        print(f"{'='*60}\n")

        for i in range(1, self.log_count + 1):
            self.buffer.archive_log()
            print(f"[Archiver]  Progress: {i}/{self.log_count} logs archived.\n")

        print(f"[Archiver]  All {self.log_count} logs archived. Archiver exiting.")


def main():
    LOG_COUNT = 5
    buffer = LogBuffer()

    # Initialize and start threads
    gen = LogGenerator(buffer, LOG_COUNT)
    arc = LogArchiver(buffer, LOG_COUNT)

    gen.start()
    arc.start()

    gen.join()
    arc.join()
    print("\nLog Maintenance Complete.")

if __name__ == "__main__":
    main()
