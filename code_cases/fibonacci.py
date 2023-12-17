import random
class TestCase:
    cache = {}
    def fn(self, x):
        if x in (1,2):
            return 1
        if x in self.cache:
            return self.cache[x]
        self.cache[x] = self.fn(x-1) + self.fn(x-2)
        return self.cache[x]
    
    def gen_test_case(self):
        inputs = list(range(26, 36))
        cases = []
        for i in inputs:
            cases.append((i, self.fn(i)))
        return cases

