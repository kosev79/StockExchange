from exchange import StockExchange


def start_trading():
    stock_exchange = StockExchange()
    while True:
        command = input("Action: ")

        valid, error = stock_exchange.validate_command(command)
        if not valid:
            print(error)
            continue

        parts = command.split()

        if parts[0].upper() == "QUIT":
            print("No output")
            break

        result = stock_exchange.process_command(command)
        if result is not None:
            print(result)
