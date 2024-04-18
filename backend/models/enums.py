from enum import Enum

class MuscleGroup(str, Enum):
    CHEST = "Chest"
    BACK = "Back"
    SHOULDERS = "Shoulders"
    BICEPS = "Biceps"
    TRICEPS = "Triceps"
    LEGS = "Legs"
    QUADRICEPS = "Quadriceps"
    HAMSTRINGS = "Hamstrings"
    CALVES = "Calves"
    GLUTES = "Glutes"
    ABDOMINALS = "Abdominals"
    FOREARMS = "Forearms" 
    OBLIQUES = "Obliques"
    LATS = "Lats"

class BandColor(str, Enum):
    YELLOW = "yellow"
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    BLACK = "black"
    PURPLE = "purple"
    ORANGE = "orange"
    GRAY = "gray"

class ResistanceType(str, Enum):
    DUMBBELL = "Dumbbell"
    BARBELL = "Barbell"
    BAND = "Band"
    BODYWEIGHT = "Bodyweight"

class WeightUnits(str, Enum):
    KILOGRAMS = "kg"
    LBS = "lbs"
    
class HeightUnits(str, Enum):
    IMPERIAL = "imperial"
    METRIC = "metric"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"