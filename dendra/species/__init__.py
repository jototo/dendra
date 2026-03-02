from dendra.species.base import TreeSpec
from dendra.species import (
    redbud,
    pine,
    white_oak,
    dogwood,
    cedar,
    sycamore,
    pawpaw,
    persimmon,
)

SPECIES: dict[str, TreeSpec] = {
    "redbud": redbud.spec,
    "pine": pine.spec,
    "white-oak": white_oak.spec,
    "dogwood": dogwood.spec,
    "cedar": cedar.spec,
    "sycamore": sycamore.spec,
    "pawpaw": pawpaw.spec,
    "persimmon": persimmon.spec,
}
