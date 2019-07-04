from decimal import Decimal
import sys


FOLD_AVAILABLE = sys.version_info >= (3, 6)

number_types = (int, float, Decimal)
