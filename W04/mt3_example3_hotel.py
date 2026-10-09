"""
Metamorphic testing demo for MT III, Example 3: A hotel search system.

A query has four parts: the stay (check-in and check-out dates), a price range per night,
a city, and a maximum distance from the city GPO. The answer is a set of hotels.
Nobody can check that set directly, so the MRs compare the answers of related queries.

The six hotels below are made up for the demo. A hotel matches a query when it is in the
city, within the distance, inside the price range, and free on every night of the stay.
"""

from dataclasses import dataclass, replace
from datetime import date, timedelta

ONE_NIGHT = timedelta(days=1)


def december(day):
    return date(2020, 12, day)


@dataclass(frozen=True)
class Hotel:
    name: str
    city: str
    km_from_gpo: float  # Distance from the GPO of its own city.
    price: int  # Room charge per night in USD.
    free_nights: frozenset  # Nights with a free room.


@dataclass(frozen=True)
class Query:
    check_in: date
    check_out: date
    price_min: int
    price_max: int
    city: str
    max_km: float

    # Dec 15-16 means check in on Dec 15 and check out on Dec 16: one night, Dec 15.
    def nights(self):
        return [
            self.check_in + timedelta(days=i)
            for i in range((self.check_out - self.check_in).days)
        ]

    def __str__(self):
        return (
            f"{self.check_in:%b} {self.check_in.day}-{self.check_out.day}, "
            f"{self.price_min}-{self.price_max} USD, {self.city}, {self.max_km:g} km"
        )


HOTELS = [
    Hotel(
        "A", "Melbourne", 5, 120, frozenset(december(day) for day in (13, 14, 15, 16))
    ),
    Hotel("B", "Melbourne", 8, 200, frozenset(december(day) for day in (15, 16))),
    Hotel(
        "C", "Melbourne", 12, 240, frozenset(december(day) for day in (12, 13, 14, 15))
    ),
    Hotel(
        "D", "Melbourne", 6, 280, frozenset(december(day) for day in (14, 15, 16, 17))
    ),
    Hotel("E", "Melbourne", 10, 150, frozenset(december(day) for day in (13, 14, 16))),
    Hotel("F", "Sydney", 3, 180, frozenset(december(day) for day in range(12, 19))),
]

OTHER_CITY = {"Melbourne": "Sydney", "Sydney": "Melbourne"}  # About 700 km apart.

# Five source inputs, so every MR gets five metamorphic groups. The first one is the lecture example.
SOURCE_INPUTS = [
    Query(december(15), december(16), 100, 250, "Melbourne", 15),
    Query(december(13), december(14), 100, 250, "Melbourne", 12),
    Query(december(16), december(17), 150, 300, "Melbourne", 10),
    Query(december(14), december(16), 100, 300, "Melbourne", 15),
    Query(december(15), december(16), 100, 250, "Sydney", 15),
]


# Programs under test. The first one is correct, the other two contain one fault each.


def search_correct(query):
    return {
        hotel.name
        for hotel in HOTELS
        if hotel.city == query.city
        and hotel.km_from_gpo <= query.max_km
        and query.price_min <= hotel.price <= query.price_max
        and all(night in hotel.free_nights for night in query.nights())
    }


# Fault: a free room is checked for the check-in night only.
def search_checks_first_night_only(query):
    return {
        hotel.name
        for hotel in HOTELS
        if hotel.city == query.city
        and hotel.km_from_gpo <= query.max_km
        and query.price_min <= hotel.price <= query.price_max
        and query.check_in in hotel.free_nights
    }


# Fault: the city is never compared, so a hotel close to any GPO matches.
def search_ignores_city(query):
    return {
        hotel.name
        for hotel in HOTELS
        if hotel.km_from_gpo <= query.max_km
        and query.price_min <= hotel.price <= query.price_max
        and all(night in hotel.free_nights for night in query.nights())
    }


PROGRAMS = [search_correct, search_checks_first_night_only, search_ignores_city]


# The result of checking one MR on one metamorphic group.
@dataclass
class Check:
    relation: str  # The relation that FO and SO must satisfy.
    rows: list  # One (input label, input, output label, output) tuple per execution.
    holds: bool


# Metamorphic relations. Each one changes one part of SI and keeps the other parts.


def mr1_longer_stay(program, si):
    fi = replace(si, check_in=si.check_in - ONE_NIGHT)  # Dec 15-16 becomes Dec 14-16.
    so, fo = program(si), program(fi)
    return Check(
        "FO is a subset of SO",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        fo.issubset(so),
    )


def mr2_wider_price_range(program, si):
    fi = replace(si, price_max=si.price_max + 50)
    so, fo = program(si), program(fi)
    return Check(
        "FO is a superset of SO",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        fo.issuperset(so),
    )


def mr3_distant_city(program, si):
    fi = replace(si, city=OTHER_CITY[si.city])
    so, fo = program(si), program(fi)
    return Check(
        "FO and SO have no hotel in common",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        fo.isdisjoint(so),
    )


def mr4_smaller_distance(program, si):
    fi = replace(si, max_km=si.max_km - 6)  # 15 km becomes 9 km.
    so, fo = program(si), program(fi)
    return Check(
        "FO is a subset of SO",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        fo.issubset(so),
    )


def mr5_join_two_stays(program, si):
    stay = si.check_out - si.check_in
    si_1 = si
    si_2 = replace(
        si, check_in=si.check_in - stay, check_out=si.check_in
    )  # The stay just before SI-1.
    fi = replace(si, check_in=si_2.check_in)  # Both stays as one booking.
    so_1, so_2, fo = program(si_1), program(si_2), program(fi)
    return Check(
        "FO is a subset of both SO-1 and SO-2",
        [
            ("SI-1", si_1, "SO-1", so_1),
            ("SI-2", si_2, "SO-2", so_2),
            ("FI", fi, "FO", fo),
        ],
        fo.issubset(so_1) and fo.issubset(so_2),
    )


MRS = [
    ("MR1 Longer stay", mr1_longer_stay),
    ("MR2 Wider price range", mr2_wider_price_range),
    ("MR3 Distant city", mr3_distant_city),
    ("MR4 Smaller distance", mr4_smaller_distance),
    ("MR5 Join two stays", mr5_join_two_stays),
]


# Printing.


def show(value):
    if isinstance(value, (set, frozenset)):
        return "{" + ", ".join(sorted(value)) + "}"
    return str(value)


def print_check(name, check, indent="  "):
    verdict = "satisfied" if check.holds else "VIOLATED"
    print(f"{indent}{name}, expect {check.relation}: {verdict}")
    width = max(len(show(row[1])) for row in check.rows)
    for input_label, input_value, output_label, output_value in check.rows:
        print(
            f"{indent}    {input_label:<4} = {show(input_value):<{width}}    {output_label:<4} = {show(output_value)}"
        )


def show_step_1():
    correct = PROGRAMS[0]
    print(
        f"Step 1. Every MR holds for the correct program ({correct.__name__}) on the first source input"
    )
    for name, mr in MRS:
        print_check(name, mr(correct, SOURCE_INPUTS[0]))


def show_not_an_mr():
    si = SOURCE_INPUTS[0]
    fi = replace(
        si, check_in=si.check_in - ONE_NIGHT, check_out=si.check_out - ONE_NIGHT
    )
    so, fo = search_correct(si), search_correct(fi)
    print("Not an MR: move the stay one night earlier, correct program")
    print(f"      SI   = {show(si)}    SO   = {show(so)}")
    print(f"      FI   = {show(fi)}    FO   = {show(fo)}")
    print(
        f"      {show(so - fo)} dropped out and {show(fo - so)} came in, so FO and SO have no fixed relation"
    )


def show_step_2():
    print(
        f"Step 2. Violated metamorphic groups out of {len(SOURCE_INPUTS)} for each MR (0 = fault not revealed)"
    )
    width = max(len(program.__name__) for program in PROGRAMS) + 2
    print("  " + " " * width + "".join(f"{name.split()[0]:>5}" for name, _ in MRS))
    for program in PROGRAMS:
        counts = [
            sum(not mr(program, si).holds for si in SOURCE_INPUTS) for _, mr in MRS
        ]
        print(
            f"  {program.__name__:<{width}}"
            + "".join(f"{count:>5}" for count in counts)
        )


def first_violation(program):
    for name, mr in MRS:
        for si in SOURCE_INPUTS:
            check = mr(program, si)
            if not check.holds:
                return name, check
    return None


def show_step_3():
    print("Step 3. The first violation found for each faulty program")
    for program in PROGRAMS[1:]:
        print(f"  {program.__name__}:")
        found = first_violation(program)
        if found is None:
            print("      no MR revealed this fault")
        else:
            print_check(*found, indent="    ")


if __name__ == "__main__":
    print("MT III, Example 3: A hotel search system\n")
    show_step_1()
    print()
    show_not_an_mr()
    print()
    show_step_2()
    print()
    show_step_3()
