from exchange import StockExchange


def start_trading():
    stock_exchange = StockExchange()
    while True:
        command = input("Action: ")
        valid, error = stock_exchange.validate_command(command)
        parts = command.split()
        if not valid:
            print(error)
            continue
        if parts[0].upper() == "QUIT":
            print("No output")
            break

        order = stock_exchange.process_command(command)
        if order:
            print(order)
