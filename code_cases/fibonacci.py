#%%
import random
class TestCase:
    def fn(self, x):
        ''' # Example
        import sys
        sys.set_int_max_str_digits(1000000)
        c = TestCase()
        c.fn(1000000)
        '''
        return self.m(x)
    
    def gen_test_case(self):
        inputs = list(range(26, 36))
        cases = []
        for i in inputs:
            cases.append((i, self.fn(i)))
        return cases

    def m(self, n):
        init_matrix = [
            [1, 1], 
            [1, 0]
        ] if n >= 0 else [
            [0, 1], 
            [1, -1]
        ]
        ans = self.matrix_n_power(init_matrix, abs(n))
        
        return ans[0][1]
            
    def multiple_matrix(self, A, B):
        ''' Calculate AB '''
        C = [[0 for _ in range(len(A))] for _ in range(len(B[0]))]
        for i in range(len(A)):
            for j in range(len(B[0])):
                dot_ab = 0
                for k in range(len(B)):
                    dot_ab += A[i][k] *B[k][j]
                C[i][j] = dot_ab
        return C
    
    def matrix_n_power(self, M, n):
        ''' calculate M^n '''
        if n == 0:
            return [
                [1, 0], 
                [0, 1]
            ]
        elif n == 1:
            return M
        else:
            tmp = self.matrix_n_power(M, n //2)
            final = self.multiple_matrix(tmp, tmp)
            if n % 2 != 0:
                return self.multiple_matrix(final, M)
        return final
