import datetime as dt
from fractions import Fraction
class fractional_interval:
    """
    `fractional_interval` objects allow creation of intervals of fractions 
    which native interval class do not allow. 
    
    This is useful to know whether a point is precisely (i.e. avoid floating
    point quirks) within an interval or not. 
    
    Also has convenience methods to access whether a point is in a range and 
    how much of an interval a point .
    """
    def __init__(self, left: Fraction, right: Fraction, closed: str):
        if (left > right):
            raise ValueError((
                f'{left}(the left bound) is greater than {right} '
                f'(the right bound). Please swap the left and right '
                f'bounds if you wish to create an interval with '
                f'these two values.'
            ))
        self.left = left
        self.right = right
        self.closed = closed

    def __repr__(self):
        if self.closed == 'left':
            li = '['
            ri = ')'
        elif self.closed == 'right':
            li = '('
            ri = ']'
        elif self.closed == 'both':
            li = '['
            ri = ']'
        elif self.closed == 'none':
            li = '('
            ri = ')'
        return f'{li}{self.left}, {self.right}{ri}'

    def __eq__(self, other):
        return (self.left, self.right) == (other.left, other.right)

    def point_in_range_coverage(self, point: float) -> float:
        '''
        Measure how far `point` lies within the interval [left, right].

        Values below `left` map to 0.0.
        Values above `right` map to 1.0.
        Values inside the interval are mapped linearly to (0.0, 1.0).

        Effectively computes a clamped linear normalization.

        This can be useful to compute how much of a nakṣatra is covered by a 
        seed graha at the time of birth.

        Args:
            point (float): The value to evaluate.

        Returns (float):        
            A number between 0.0 and 1.0 indicating the relative
            position of `point` within the interval.
        '''
        point = Fraction(point)
        if point <= self.left:
            return 0
        if point >= self.right:
            return 1
        else:
            out = (point - self.left)/(self.right - self.left)
            return float(out)

    def isin(self, point: float) -> bool:
        '''
        Computes whether a point lie within an interval.

        Args:
            point (float): The value which may or may not lie in the interval
        
        Returns (bool):
            A bool value indicating whether or not the point lies in the 
            interval.
        '''
        if self.closed in ['left', 'both']:
            left_in = point >= self.left
        if self.closed in ['right', 'none']:
            left_in = point > self.left
        if self.closed in ['right', 'both']:
            right_in = self.right >= point
        if self.closed in ['left', 'none']:
            right_in = self.right > point
        return (left_in & right_in)
