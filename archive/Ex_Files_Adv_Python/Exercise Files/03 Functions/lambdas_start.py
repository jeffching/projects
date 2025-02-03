# Use lambdas as in-place functions


def CelsisusToFahrenheit(temp):
    return (temp * 9/5) + 32


def FahrenheitToCelsisus(temp):
    return (temp-32) * 5/9


def main():
    ctemps = [0, 12, 34, 100]
    ftemps = [32, 65, 100, 212]

    # TODO: Use regular functions to convert temps
    ftemps_toc = list(map(FahrenheitToCelsisus,ftemps))
    #print(ftemps_toc)
    ctemps_tof = list(map(CelsisusToFahrenheit,ctemps))
    #print(ctemps_tof)

    # TODO: Use lambdas to accomplish the same thing
    print(list(map(lambda t: (t-32) * 5/9,ftemps)))
    print(list(map(lambda t: (t* 9/5) + 32,ctemps)))

if __name__ == "__main__":
    main()
