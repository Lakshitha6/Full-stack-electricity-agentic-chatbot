import random

def generate_electricity_id() -> str :
    """
    Generates a unique electricity ID by generating random digits.

    Returns:
        str: Unique electricity ID.    

    """

    return f"ELEC-{random.randint(100000, 999999)}"