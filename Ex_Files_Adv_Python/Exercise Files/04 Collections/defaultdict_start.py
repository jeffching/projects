# Demonstrate the usage of defaultdict objects
from collections import defaultdict

def main():
    # define a list of items that we want to count
    fruits = ['apple', 'pear', 'orange', 'banana',
              'apple', 'grape', 'banana', 'banana']

    # use a dictionary to count each element
    #fruitCounter = {}
    #fruitCounter = defaultdict(int)
    fruitCounter = defaultdict(lambda : 100) #starts at 100

    # Count the elements in the list
    for fruit in fruits: 
        #fruitCounter[fruit] += 1 #this fails because the key has not been added yet (need orderedDict)
        fruitCounter[fruit] += 1

    # print the result
    for (k, v) in fruitCounter.items():
        print(k + ": " + str(v))

    # if you have a situation where the fact that a key is missing from the dictionary is an important indicator, then default dict is probably not the right collection to use.

if __name__ == "__main__":
    main()
