import threading

class ThreadSafeList:
    def __init__(self):
        self.inner_list = []
        self.lock = threading.Lock()


    def append(self, item):
        with self.lock:
            self.inner_list.append(item)
            print("Append player ", item.user.username)
            print("Len of inner ", len(self.inner_list))


    def pop(self, index=-1):
        with self.lock:
            if index == -1:
                return self.inner_list.pop()
            else:
                item = self.inner_list[index]
                del self.inner_list[index]
                return item
            
    
    def remove_items(self, items: list):
        with self.lock:
            print("Remove players ", items)
            for i in items:
                self.inner_list.remove(i)


    def __getitem__(self, index):
        with self.lock:
            return self.inner_list[index]


    def __len__(self):
        with self.lock:
            print("Inner list len ", len(self.inner_list))
            return len(self.inner_list)


    def __str__(self):
        with self.lock:
            return str(self.inner_list)
        

