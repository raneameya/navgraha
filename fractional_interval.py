from fractions import Fraction
class fractional_interval:
    """A class to accommodate intervals of fractions"""
    def __init__(self, left: Fraction, right: Fraction, closed: str):
        if (left > right):
            raise ValueError((
                f'{left}(the left bound) is greater than {right} '
                f'(the right bound). Please swap the left and right '
                f'bounds if you wish to create an interval with '
                f'these two values.'
            ))
        self.left=left
        self.right=right
        self.closed=closed
    
    def __str__(self):
        if self.closed=='left':
            li = '['
            ri = ')'
        elif self.closed=='right':
            li = '('
            ri = ']'
        elif self.closed=='both':
            li = '['
            ri = ']'
        elif self.closed=='none':
            li = '('
            ri = ')'
        return f'{li}{self.left}, {self.right}{ri}'

    def point_in_range_coverage(self, point):
        # Useful to compute how much of a dasha is over
        point = Fraction(point)
        if point <= self.left:
            return 0
        if point >= self.right:
            return 1
        else:
            out = (point - self.left)/(self.right - self.left)
            return float(out)