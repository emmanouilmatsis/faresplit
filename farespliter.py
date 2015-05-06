import decimal


class User:

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        self.__balance = decimal.Decimal(value)

    def __init__(self, name, balance):
        self.name = name
        self.balance = balance


class Transaction:

    @property
    def payer(self):
        return self.__payer

    @payer.setter
    def payer(self, value):
        self.__payer = value

    @property
    def payee(self):
        return self.__payee

    @payee.setter
    def payee(self, value):
        self.__payee = value

    @property
    def amount(self):
        return self.__amount

    @amount.setter
    def amount(self, value):
        self.__amount = decimal.Decimal(value)

    def __init__(self, payer, payee, amount):
        self.payer = payer
        self.payee = payee
        self.amount = amount


class Farespliter:

    def faresplit(self, transactions):
        users = self.__users(transactions)
        transactions = self.__transactions(users)
        return transactions

    def __users(self, transactions):
        users = []

        for transaction in transactions:
            for payer in users:
                if payer.name == transaction.payer:
                    payer.balance += transaction.amount
                    break
            else:
                payer = User(transaction.payer, transaction.amount)
                users.append(payer)

            if transaction.payee != "*":
                for payee in users:
                    if payee.name == transaction.payee:
                        payee.balance -= transaction.amount
                        break
                else:
                    payee = User(transaction.payee, transaction.amount)
                    users.append(payee)

        total = sum(user.balance for user in users)

        for user in users:
            user.balance -= total / len(users)
            print(user.name, user.balance)

        return users

    def __transactions(self, users):
        transactions = []

        n = len(users)

        i = 1
        while i < n:
            j = 0
            while j < n - i:

                if users[j].balance > users[j+i].balance: #XXX: borrower is negativve
                    users[j], users[j+i] = users[j+i], users[j]

                transaction = Transaction(users[j].name, users[j+i].name, users[j+i].balance)
                transactions.append(transaction)

                users[j].balance += users[j+i].balance
                users[j+i].balance += -users[j+i].balance

                j += 2 * i
            i *= 2

        return transactions
