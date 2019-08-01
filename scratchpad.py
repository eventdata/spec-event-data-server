from datetime import datetime


class Stopwatch:

    def __init__(self):
        self.is_running = False
        self.start = None
        self.end = None

    def begin(self):
        if self.is_running:
            self.stop()
        self.start = datetime.now()
        self.is_running = True

    def end(self):
        if not self.is_running:
            raise ValueError("Clock is already stopped")
        self.stop = datetime.now()
        self.is_running = False

    def elapsed_seconds(self):
        return (self.stop-self.start).total_seconds()

clock = Stopwatch()

print type(clock)

clock.start()


clock.stop()

print clock.elapsed_seconds()