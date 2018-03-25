import random


class Sample:
    def init_fun(self, n):
        new_list = []
        for i in range(n):
            new_list.append(random.randint(1, 10000))
        return new_list

    def fun(self, nlist):
        sorted(nlist)

    def cleaner(self):
        pass
