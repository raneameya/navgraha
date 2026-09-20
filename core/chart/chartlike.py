from typing import Protocol

from core.sweadaptor.swisseph_adaptor import SwissEphAdaptor

class ChartLike(Protocol):
    swisseph_adaptor: SwissEphAdaptor
