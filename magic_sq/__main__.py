import logging
import sys
import time

from argparse import ArgumentParser
from itertools import count
from multiprocessing import Pool

logger = logging.getLogger(__name__)


from . import test



def main(n=None, start=2, multiprocessing=True):
    """
    Search for a magic square of squares (bimagic square of order 3)

    For this code, the model of the problem is as follows:
        a**2 b**2 c**2
        d**2 e**2 f**2
        g**2 h**2 i**2

    To start to understand this, first lets build a list of equations that 
        are used in this problem:

    a**2 + b**2 + c**2 = k
    d**2 + e**2 + f**2 = k
    g**2 + h**2 + i**2 = k
    a**2 + d**2 + g**2 = k
    b**2 + e**2 + h**2 = k
    c**2 + f**2 + i**2 = k
    a**2 + e**2 + i**2 = k
    c**2 + e**2 + g**2 = k

    Looking at this I first noted that you could set a**2 + b**2 + c**2 = a**2 + d**2 + g**2 (or some rotation),
        and remove the a**2 to get b**2 + c**2 = d**2 + g**2

    It stood out to me that the essence of solving this algorithm could be finding co-equal pairs of numbers that
        satisfy this equality. 

    Then the problem becomes, how do I take 2 pairs of solutions and join them together into the outside and inside
        areas. However it quickly stood out that the best way to join them up would be not to visualize joining them
        on the outside areas, but instead join them in the middle using `e` since that is the most important variable
        (it is used in the most equations above).

    So: If I could find 4 total solutions to x**2 + y**2 that are all unique and equal, then I can arrange them such as
        pairs: (a1, a2), (b1, b2), (c1, c2), (d1, d2)

        a1**2 b1**2 c1**2
        d1**2 e**2  d2**2
        c2**2 b2**2 a2**2

    Doing this method, I can take the 4 directions:
        a1**2 + e**2 + a2**2 (diagonal)
        c1**2 + e**2 + c2**2 (diagonal)
        b1**2 + e**2 + b2**2 (center)
        d1**2 + e**2 + d2**2 (middle)

    and be guarenteed they are all already equal for any value of e. Halfway there...

    Futhermore, we can compute an e using the top row by doing `e = sqrt((a1**2 + b1**2 + c1**2) - (d1**2 + d2**2))`
        This will also ensure that the top row's value (a**2 + b**2 + c**2 above) will match the above 4 values

    The next step is simply to verify the remaining 3 directions for any potential solutions. They are:
        a**2 + d**2 + g**2 (left column)
        c**2 + f**2 + i**2 (right column)
        g**2 + h**2 + i**2 (bottom row)

    I have only added a check for the bottom row however, and to date,
        no potential solutions have made it passed that point...

    Hooray: With the above python methods, the datastore is no longer needed! The memory requirements are solved, 
        AND I can make this multiprocessing AND it gets done in 0.5s what took an entire night before!!
    """
    # dual_sum -> unique_pairs
    iterator = count(start) if n is None else range(start, n)

    if multiprocessing:
        with Pool() as tp:
            for i, _ in enumerate(tp.imap(test, iterator, chunksize=10**4), start=start):
                if i % 10**5 == 0:
                    logger.info('Passing %s', i)
    else:
        for i in iterator:
            test(i)

            if i % 10**5 == 0:
                logger.info('Passing %s', i)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('end', type=int, default=None, nargs='?')
    parser.add_argument('--start', type=int, default=2, 
                        help="The start point. Be VERY careful to start well below the last end point, "
                             "or a solution may be missed.")

    args = parser.parse_args()

    _stream = logging.StreamHandler(sys.stdout)
    _stream.setLevel(logging.INFO)
    _stream.setFormatter(logging.Formatter('%(message)s'))
    _file = logging.FileHandler('the.log')
    _file.setLevel(logging.DEBUG)
    _file.setFormatter(logging.Formatter('%(module)s::%(funcName)s::%(lineno)d %(levelname)s %(asctime)s - %(message)s'))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_stream)
    logger.addHandler(_file)

    logger.info('Starting with end=%s at start=%s', args.end, args.start)
    start_time = time.time()
    main(args.end, args.start)
    end_time = time.time()
    logger.info('Took %s', end_time - start_time)
