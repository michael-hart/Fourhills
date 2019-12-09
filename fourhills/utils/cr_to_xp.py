from fourhills.exceptions import FourhillsExperienceLookupError


CR_XP_LUT = {
    0.0: 10,
    0.125: 25,
    0.25: 50,
    0.5: 100,
    1.0: 200,
    2.0: 450,
    3.0: 700,
    4.0: 1100,
    5.0: 1800,
    6.0: 2300,
    7.0: 2900,
    8.0: 3900,
    9.0: 5000,
    10.0: 5900,
    11.0: 7200,
    12.0: 8400,
    13.0: 10000,
    14.0: 11500,
    15.0: 13000,
    16.0: 15000,
    17.0: 18000,
    18.0: 20000,
    19.0: 22000,
    20.0: 25000,
    21.0: 33000,
    22.0: 41000,
    23.0: 50000,
    24.0: 62000,
    25.0: 75000,
    26.0: 90000,
    27.0: 105000,
    28.0: 120000,
    29.0: 135000,
    30.0: 155000,
}


def cr_to_xp(cr: float) -> int:
    cr = float(cr)
    if cr < 0.0:
        raise FourhillsExperienceLookupError(
            f"Challenge rating is too low to provide experience: {cr}"
        )
    max_cr = list(CR_XP_LUT.keys())[-1]
    if cr > max_cr:
        raise FourhillsExperienceLookupError(
            f"Challenge rating is too high to provide experience: {cr}. "
            f"Highest supported challenge rating is {max_cr}."
        )

    if cr in CR_XP_LUT:
        return CR_XP_LUT[cr]

    # Linear interpolation will for other challenge ratings
    for key, val in CR_XP_LUT.items():
        if key < cr:
            lower = (key, val)
        if key > cr:
            upper = (key, val)
            break

    ratio = (cr - lower[0]) / (upper[0] - lower[0])
    additional_xp = ratio * (upper[1] - lower[1])
    xp = lower[1] + additional_xp
    return xp
