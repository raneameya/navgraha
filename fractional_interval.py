import datetime as dt
from fractions import Fraction
class fractional_interval:
    """
    A class to accommodate intervals of fractions. This would be useful in 
    cases where dashas need to be computed
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
    
    def __str__(self):
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

    def point_in_range_coverage(self, point):
        '''
        Computes how "far" a point is, in an interval, with defaults of 100% 
        if the point is beyond interval.right and 0% if point is less than 
        interval.left.
        This is useful to compute how much of a dasha is over.
        '''
        point = Fraction(point)
        if point <= self.left:
            return 0
        if point >= self.right:
            return 1
        else:
            out = (point - self.left)/(self.right - self.left)
            return float(out)
    
    def isin(self, point: float):
        '''
        Does a point lie within an interval
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

def get_endpoints_from_point_coverage(
    point: float, coverage: float, interval_length
):
    '''
    Compute a fractional interval given a point, the %age covered by the 
    point in the desired interval and the length of the interval. If the 
    length of the interval is a timedelta, the interval is returned as a 
    tuple of start and end times.
    '''
    left = point - (coverage * interval_length)
    right = left + interval_length
    return (left, right)
