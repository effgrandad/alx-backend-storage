#!/usr/bin/env python3

'''
A straightforward module that includes practice
projects on using Reddis for caching and the Redis
client in Python
'''

from redis import Redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''
    A decorator that keeps track of a function's call count
    and stores it in cache
    Args:
        method (Callable): The function to keep tabs on
    Returns:
        Returns a callable
    '''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''
        The callback that gets returned when calling decorator
        Args:
            args(list): A list of arguments
            kwargs(dict): A dictionary of keyworded args
        Returns:
            returns the return value of calling the `method`
            method, passing in the args passed to this function
        '''
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    '''
    A decorator to monitor a function when its called
    Args:
        method (Callable): The callable object
    Returns:
        Returns a callable
    '''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_string = str(args)
        self._redis.rpush(f"{method.__qualname__}:inputs", input_string)
        output_string = str(method(self, *args, **kwargs))
        self._redis.rpush(f"{method.__qualname__}:outputs", output_string)
        return output_string

    return wrapper


def replay(fn: Callable):
    '''
    Call a function a bunch of times
    Args:
        fn (Callable): The callback function
    '''
    mem = Redis()
    func_name_qual = fn.__qualname__
    value = int(mem.get(func_name_qual) or b"0")
    print(f"{func_name_qual} was called {value} times:")
    inputs = mem.lrange(f"{func_name_qual}:inputs", 0, -1)
    outputs = mem.lrange(f"{func_name_qual}:outputs", 0, -1)

    for input_bytes, output_bytes in zip(inputs, outputs):
        input_string = input_bytes.decode("utf-8")
        output_string = output_bytes.decode("utf-8")
        print(f"{func_name_qual}(*{input_string}) -> {output_string}")


class Cache:
    '''
    A cache class
    '''
    def __init__(self):
        '''
        The default constructor
        '''
        self._redis = Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''
        Store an item in the memory
        Args:
            data (Union): The item to be stored
        '''
        store_key = str(uuid4())
        self._redis.set(store_key, data)
        return store_key

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        '''
        Retrieve stored item from memory
        Args:
            key: the item to be retrieved
        fn (Callable): The callback function
        '''
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        '''
        string representation of a stored value in memory
        Args:
            key (str): Key to the item to retrieve
        '''
        value = self._redis.get(key)
        return value.decode("utf-8")

    def get_int(self, key: str) -> int:
        '''
        Get int helper function
        Args:
            key (str): The key to the value to retrieve
        Returns:
            retuns an int
        '''
        value = self._redis.get(key)
        return int(value.decode("utf-8", errors="ignore") or 0)
