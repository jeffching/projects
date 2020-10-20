# demonstrate template string functions

from string import Template
def main():
    # Usual string formatting with format()
    str1 = "You're watching {0} by {1}".format("Advanced Python", "Joe Marini")
    print(str1)
    
    # TODO: create a template with placeholders
    templ = Template("You're watching ${title} by ${author}")
    # TODO: use the substitute method with keyword arguments
    str2 = templ.substitute(title="Kumo Bear",author="Rilakumma")
    # TODO: use the substitute method with a dictionary
    str3 = templ.substitute({"title":"Kumo Bear","author":"Jeff"})
    print(str2)
    print(str3)
    
if __name__ == "__main__":
    main()
    