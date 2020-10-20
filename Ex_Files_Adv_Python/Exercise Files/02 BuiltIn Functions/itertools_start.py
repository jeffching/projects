# advanced iteration functions in the itertools package
import itertools

def testFunction(x):
    return x < 40
    #pass


def main():
    # TODO: cycle iterator can be used to cycle over a collection
    seq1 = ["Joe", "John", "Mike"]
    cycle = itertools.cycle(seq1)
    #print(next(cycle))
    #print(next(cycle))
    #print(next(cycle))
    #print(next(cycle)) #once complete a cycle, goes back to beginning of list
    #print(next(cycle)) 
#
    # TODO: use count to create a simple counter
    count = itertools.count(100,10)
    #print(next(count))
    #print(next(count))
    #print(next(count))
    #print(next(count))
    #print(next(count))


    # TODO: accumulate creates an iterator that accumulates values
    vals = [10,20,30,40,50,40,30]
    #acc = list(itertools.accumulate(vals,max))
    #print(list(acc)) 
    #doesn't seem to work...
            
    # TODO: use chain to connect sequences together
    x = itertools.chain("ABCD","1234")
    print(list(x)) #['A', 'B', 'C', 'D', '1', '2', '3', '4']
    
    # TODO: dropwhile and takewhile will return values until
    # a certain condition is met that stops them

    # dropwhile will drop values from the sequence while the test function returns true, 
    # and then it will start returning every value after that. And then takewhile is the opposite. It will return values from the sequence while the predicate function returns true, and then it will stop giving you values.
    print(list(itertools.dropwhile(testFunction,vals))) #i.e. while-continue loop
    print(list(itertools.takewhile(testFunction,vals))) #i.e. while loop
    
if __name__ == "__main__":
    main()
    