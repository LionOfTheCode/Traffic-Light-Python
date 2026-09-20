class CircularQueue:
    """
    This class represents a circular queue data structure with a fixed capacity.
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = 0
        self.rear = 0
        self.size = 0

    def __len__(self):
        return self.size

    def __iter__(self):
        for i in range(self.size):
            index = (self.front + i) % self.capacity
            yield self.queue[index]

    def is_empty(self) -> bool:
        return self.size == 0

    def is_full(self) -> bool:
        return self.size == self.capacity

    def enqueue(self, item):
        if self.is_full():
            raise OverflowError("Queue is full")
        self.queue[self.rear] = item
        self.rear = (self.rear + 1) % self.capacity
        self.size += 1


    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        item = self.queue[self.front]
        self.queue[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return item

    def peek_front(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.queue[self.front]

    def peek_back(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.queue[(self.rear - 1) % self.capacity]