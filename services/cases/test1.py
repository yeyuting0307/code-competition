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
    
    def get_answers(self):
        random.seed(20231212)
        inputs = list(range(1, 20))
        random.shuffle(inputs)
        ans = []
        for i in inputs:
            ans.append((i, self.fn(i)))
        return ans

