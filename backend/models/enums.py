from enum import Enum
class WeightUnits(str, Enum):
    KILOGRAMS = "kg"
    LBS = "lbs"
    
class HeightUnits(str, Enum):
    IMPERIAL = "imperial"
    METRIC = "metric"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    
# class WorkoutCategory(str, Enum):
#     UPPER = "Upper"
#     LOWER = "Lower"
#     CARDIO = "Cardio"

# class MajorMuscleGroup(str, Enum):
#     CHEST = "Chest"
#     BACK = "Back"
#     SHOULDERS = "Shoulders"
#     ARMS = "Arms"
#     CORE = "Core"
#     LEGS = "Legs"
#     HIPS = "Hips"
#     NECK = "Neck"

# class SpecificMuscleGroup(str, Enum):
#     UNSPECIFIED = "Unspecified"
#     UPPER_CHEST = "Upper Chest"
#     MIDDLE_CHEST = "Middle Chest"
#     LOWER_CHEST = "Lower Chest"
#     UPPER_BACK = "Upper Back"
#     MIDDLE_BACK = "Middle Back"
#     LOWER_BACK = "Lower Back"
#     FRONT_SHOULDER = "Front Shoulder"
#     SIDE_SHOULDER = "Side Shoulder"
#     REAR_SHOULDER = "Rear Shoulder"
#     BICEPS = "Biceps"
#     TRICEPS = "Triceps"
#     FOREARMS = "Forearms"
#     QUADRICEPS = "Quadriceps"
#     HAMSTRINGS = "Hamstrings"
#     CALVES = "Calves"
#     GLUTES = "Glutes"
#     ADDUCTORS = "Adductors"
#     ABDUCTORS = "Abductors"
#     HIP_FLEXORS = "Hip Flexors"
#     ABDOMINALS = "Abdominals"
#     OBLIQUES = "Obliques"
    
# class MovementCategory(str, Enum):
#     PRESS = "Press"
#     PULL = "Pull"
#     FLY = "Fly"
#     CURL = "Curl"
#     EXTENSION = "Extension"
#     ROTATION = "Rotation"
#     LUNGE = "Lunge"
#     SQUAT = "Squat"
#     HINGE = "Hinge"
#     ISOMETRIC = "Isometric"

# class Equipment(str, Enum):
#     DUMBBELL = "Dumbbell"
#     BARBELL = "Barbell"
#     BAND = "Band"
#     BODYWEIGHT = "Bodyweight"
#     WEIGHT_STACK_MACHINE ="Weight Stack Machine"
#     CABLE_MACHINE = "Cable Machine"
#     SMITH_MACHINE = "Smith Machine"
#     MEDICINE_BALL = "Medicine Ball"
#     KETTLEBELL = "Kettlebell"
#     EZ_BARBELL = "Ez Barbell"
#     ROPE = "Rope"
#     TRAP_BAR = "Trap Bar"
    
# class BandColor(str, Enum):
#     YELLOW = "yellow"
#     RED = "red"
#     GREEN = "green"
#     BLUE = "blue"
#     BLACK = "black"
#     PURPLE = "purple"
#     ORANGE = "orange"
#     GRAY = "gray"

