import decimal


class Service:

    def __init__(self):
        pass

    def transact(self, transaction):
        pass
        #print(id(transaction.payer), id(transaction.payee) if transaction.payee is not None else "GLOBAL", transaction.amount)


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

        print(id(payer), id(payee) if payee is not None else "*", amount)


class Mediator:

    def __init__(self, service):
        self.__service = service
        self.__colleagues = []
        self.__transactions = []

    def register(self, colleague):
        if colleague not in self.__colleagues:
            self.__colleagues.append(colleague)

    def update(self, colleague, amount):
        transaction = Transaction(colleague, None, amount)
        self.__transactions.append(transaction)

        colleague.balance -= decimal.Decimal(amount)
        for __colleague in self.__colleagues:
            if __colleague is not colleague:
                __colleague.balance += decimal.Decimal(amount) / decimal.Decimal((len(self.__colleagues) - 1))

    def faresplit(self):
        n = len(self.__colleagues)

        i = 1
        while i < n:
            j = 0
            while j < n - i:

                if self.__colleagues[j].balance < self.__colleagues[j+i].balance:
                    self.__colleagues[j], self.__colleagues[j+i] = self.__colleagues[j+i], self.__colleagues[j]

                transaction = Transaction(self.__colleagues[j], self.__colleagues[j+i], self.__colleagues[j+i].balance)
                self.__transactions.append(transaction)

                self.__colleagues[j].balance += self.__colleagues[j+i].balance
                self.__colleagues[j+i].balance += -self.__colleagues[j+i].balance

                self.__service.transact(transaction)

                j += 2 * i
            i *= 2


class Colleague:

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        self.__balance = decimal.Decimal(value)

    def __init__(self, mediator):
        self.__mediator = mediator
        self.__mediator.register(self)

        self.balance = 0

    def update(self, amount):
        self.__mediator.update(self, amount)


if __name__ == "__main__":

    service = Service()

    mediator = Mediator(service)

    colleague1 = Colleague(mediator)
    colleague2 = Colleague(mediator)

    colleague1.update('20.0')
    colleague2.update('10.0')

    print(colleague1.balance, colleague2.balance)

    mediator.faresplit()

    print(colleague1.balance, colleague2.balance)
