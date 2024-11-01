import collections
import threading

class ThreadSafeDeque:
    def __init__(self):
        self.deque = collections.deque()
        self.lock = threading.Lock()

    def append(self, item):
        with self.lock:
            self.deque.append(item)

    def pop(self, index=-1):
        with self.lock:
            if index == -1:
                return self.deque.pop()
            else:
                item = self.deque[index]
                del self.deque[index]
                return item

    def __getitem__(self, index):
        with self.lock:
            return self.deque[index]

    def __len__(self):
        with self.lock:
            return len(self.deque)

    def __str__(self):
        with self.lock:
            return str(self.deque)
        

