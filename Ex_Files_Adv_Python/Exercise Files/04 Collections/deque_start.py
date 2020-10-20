# deque objects are like double-ended queues

import collections
import string


def main():
    
    # TODO: initialize a deque with lowercase letters
    d = collections.deque(string.ascii_lowercase)
    
    # TODO: deques support the len() function
    #print(len(d))
    # TODO: deques can be iterated over
    #for elem in d:
    #    print(elem.upper())
    # TODO: manipulate items from either end
    #print(d) #no change yet!
    
    d.pop()
    d.popleft()
    d.append(2)
    d.appendleft(1)
    #print(d) #deque([1, 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 2])

    # TODO: rotate the deque
    print(d)
    d.rotate(10)
    print(d)


if __name__ == "__main__":
    main()
