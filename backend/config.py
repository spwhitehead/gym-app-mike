from dataclasses import dataclass
from models.enums import WeightUnits, HeightUnits

@dataclass
class Settings:
    weight_units: WeightUnits
    height_units: HeightUnits
    barbell_weight: int