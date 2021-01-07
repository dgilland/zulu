from decimal import Decimal
import sys


FOLD_AVAILABLE = sys.version_info >= (3, 6)

NUMBER_TYPES = (int, float, Decimal)
