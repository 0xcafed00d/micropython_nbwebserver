import utime


class CountdownTimer:
    def __init__(self, time_ms):
        self.reset(time_ms)

    def reset(self, time_ms):
        self.duration_ms = time_ms
        self.start_time = utime.ticks_ms()
        self.expired = False

    def elapsedTime(self):
        if self.hasExpired():
            return self.duration_ms
        return utime.ticks_diff(utime.ticks_ms(), self.start_time)

    def hasExpired(self):
        if not self.expired:
            self.expired = utime.ticks_diff(
                utime.ticks_ms(), self.start_time) >= self.duration_ms
        return self.expired

    def getProgress(self):
        if self.hasExpired():
            return 1.0
        return float(self.elapsedTime()) / float(self.duration_ms)
