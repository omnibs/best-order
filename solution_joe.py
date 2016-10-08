import numpy as np
from scipy.optimize import linprog
from order import BruceForce


class LinOpt(BruceForce):
    '''
    m: number of items
    n: number of sellers
    x_ij: quantity of item i from seller j
    p_ij: price of item i from seller j

    Mininimize the following:
      (p_00 * x_00) + (p_01 * x_01) + ... + (p_mn * x_mn)
    '''
    def get_m(self):
        return len(self._ctx.prices_orig)

    def get_n(self):
        return len(self._ctx.sellers)

    def get_c(self):
        '''
        Get the list of coefficients for the objective function.
        In this case, the prices are the coefficients.

        Note: c is in seller-major order
        '''
        m = self.get_m()
        n = self.get_n()
        c = np.zeros((m, n))
        for i, product_prices in enumerate(self._ctx.prices_orig):
            for j, p in enumerate(product_prices):
                c[i][j] = p
        return c.reshape(m * n)

    def get_ub_constraints(self):
        '''
        Get upper-bound inequality constraints

        A_ub is an n x (mn) matrix
        Each row represents each sellers' minimum purchase $
        Each col represents an array of variables, same as c

        b_ub is an array of length n, corresponding to the upper bound

        Note, we have to negate the values in order to create upper bound,
        since sellers have lower bound on min purchase
        '''
        m = self.get_m()
        n = self.get_n()
        A_ub = []
        b_ub = []
        # Loop over all the m sellers
        for k, seller in enumerate(self._ctx.sellers):
            c = np.zeros((m, n))
            # Loop over all the prices, which are in m x n matrix
            for i, product_prices in enumerate(self._ctx.prices_orig):
                for j, p in enumerate(product_prices):
                    if seller.id == 100 + j:
                        c[i][j] = p
            A_ub.append(c.reshape(m*n))
            b_ub.append(seller.minorder)
        return -np.array(A_ub), -np.array(b_ub)  # negate for upper bounding

    def get_eq_constraints(self):
        '''
        Get equality constraints
        '''
        m = self.get_m()
        n = self.get_n()
        c = np.zeros((m, n))
        A_eq = []
        b_eq = []
        for k, product in enumerate(self._ctx.products):
            c = np.zeros((m, n))
            # Loop over all the prices, which are in m x n matrix
            for i, product_prices in enumerate(self._ctx.prices_orig):
                for j, p in enumerate(product_prices):
                    if product.id == i:
                        c[i][j] = 1
            A_eq.append(c.reshape(m*n))
            b_eq.append(product.qty)
        return np.array(A_eq), np.array(b_eq)

    def get_bounds(self):
        bounds = []
        for i in range(self.get_m()):
            for j in range(self.get_n()):
                bounds.append((0, None))
        return bounds

    def create_order(self):
        c = self.get_c()
        A_ub, b_ub = self.get_ub_constraints()
        A_eq, b_eq = self.get_eq_constraints()
        # bounds = self.get_bounds()
        res = linprog(
            c,
            A_ub=A_ub, b_ub=b_ub,
            A_eq=A_eq, b_eq=b_eq
        )
        return res
        # res.x # values of x
        # # TODO - create order


# TODO: add shipping to objective function
