import utime


class Timeout:
    def __init__(self, time_ms):
        self.duration_ms = time_ms
        self.start_time = utime.ticks_ms()

    def hasExpired(self):
        return utime.ticks_diff(utime.ticks_ms(), self.start_time) >= self.duration_ms
