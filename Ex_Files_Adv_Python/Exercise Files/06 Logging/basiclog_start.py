# demonstrate the logging api in Python

# TODO: use the built-in logging module
import logging

def main():
    # TODO: Use basicConfig to configure logging
    logging.basicConfig(level=logging.DEBUG,
                        filename="output.log",
                        filemode="w"
                        ) #all messages are sent to the log output. it is only executed once before logging starts. instead of append by default, "w" will overwrite whatever is there already

    # Try out each of the log levels
    logging.debug("This is a debug message")
    logging.info("This is a info message")
    logging.warning("This is a warning message")
    logging.error("This is a error message")
    logging.critical("This is a critical message")

    # TODO: Output formatted strings to the log
    logging.info("here is a {} variable and an int:".format("string",10))

if __name__ == "__main__":
    main()
