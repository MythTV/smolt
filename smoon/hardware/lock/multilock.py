#! /usr/bin/python
#from __future__ import with_statement

from threading import Lock, Event
#from contextlib import contextmanager


class ReverseSemaphore(object):
    def __init__(self):
        self.counter = 0
        self.lock = Lock()
        self.event = Event()
        self.event.set()
        pass
        
    def acquire(self):
        self.lock.acquire()
        self.counter += 1
        self.event.clear()
        self.lock.release()
        pass
    
    def release(self):
        self.lock.acquire()
        self.counter -= 1
        if self.counter == 0:
            self.event.set()
            pass
        if self.counter < 0:
            self.counter = 0
            pass
        self.lock.release()
        pass
    
    def wait(self):
        return self.event.wait()
    pass


class MultiLock(object):
    def __init__(self):
        self.write_lock = Lock()
        self.read_lock = ReverseSemaphore()
        self.write_event = Event()
        self.write_event.set()
        pass
    
#    @contextmanager
#    def read_transaction(self):
#        self.read_acquire()
#        try:
#            yield
#        finally:
#            self.read_release()
#            pass
#        pass
#
#    @contextmanager
#    def write_transaction(self):
#        self.write_acquire()
#        try:
#            yield
#        finally:
#            self.write_release()
#            pass
#        pass
        
    def read_acquire(self):
        self.write_event.wait()
        self.read_lock.acquire()
        pass
    
    def read_release(self):
        self.read_lock.release()
        pass
    
    def write_acquire(self):
        self.write_lock.acquire() 
        self.write_event.clear()
        self.read_lock.wait()
        pass
    
    def write_release(self):
        self.write_event.set()
        self.write_lock.release()
        pass
    pass