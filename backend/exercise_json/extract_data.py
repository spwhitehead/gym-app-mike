import json

with open('exercise_json/exercises_json.json', 'r') as file:
    exercise_list = json.load(file)

workout_category = set()
body_parts = set()
equipment = set()
specific_muscles = set()
names = set()
target = set()
new_exercise_list = []
for i, exercise in enumerate(exercise_list):
    current_target = exercise["target"]
    target.add(current_target)
    bodyPart = exercise["bodyPart"]
    match bodyPart:
        case "upper arms" | "lower arms": 
            exercise["bodyPart"] = "arms"
            exercise["workoutCategory"] = "upper"
        case "lower legs" | "upper legs":
            exercise["bodyPart"] = "legs"
            exercise["workoutCategory"] = "lower" 
        case "cardio":
            exercise["workoutCategory"] = "cardio" 
        case "waist":
            exercise["bodyPart"] = "core"
            exercise["workoutCategory"] = "upper"
        case "neck" | "shoulders" | "back" | "chest":
            exercise["workoutCategory"] = "upper"
    exercise['description'] = exercise['instructions']
    del exercise['instructions']
    exercise["majorMuscle"] = exercise['bodyPart']
    del exercise["bodyPart"]
    
    specificMuscles = set()
    for secondary_muscle in exercise["secondaryMuscles"]:
        match secondary_muscle:
            case 'biceps' | 'glutes' | 'triceps' | 'hamstrings' | 'obliques' | 'hip flexors' | 'lower back' | 'upper chest' | 'calves':
                specificMuscles.add(secondary_muscle)
            case 'brachialis':
                specificMuscles.add('biceps')
            case 'shoulders' | 'deltoids':
                specificMuscles.add("front shoulder")
            case 'upper back' | 'trapezius' | 'rhomboids' | 'traps':
                specificMuscles.add("upper back")
            case 'groin' | 'inner thighs':
                specificMuscles.add("adductors")
            case 'lower abs' | 'abdominals' | 'core':
                specificMuscles.add("abdominals")
            case 'lats' | 'latissimus dorsi':
                specificMuscles.add("middle back")
            case 'chest':
                specificMuscles.add("middle chest")
            case 'wrist extensors' | 'hands' | 'grip muscles' | 'wrists' | 'wrist flexors' | 'forearms':
                specificMuscles.add("forearms")
            case 'back':
                specificMuscles.add("middle back")
            case 'sternocleidomastoid' | 'rotator cuff' | 'feet' | 'soleus' | 'shins' | 'ankle stabilizers' | _:
                specificMuscles.add("unspecified")
                
    match exercise['target']:
        case 'glutes' | 'hamstrings' | 'abductors' | 'adductors' | 'calves' | 'triceps' | 'biceps' | 'forearms' | 'upper back':
            specificMuscles.add(exercise['target'])
        case 'pectorals':
            specificMuscles.add("middle chest")
        case 'quads':
            specificMuscles.add("quadriceps")
        case 'serratus anterior':
            specificMuscles.add("middle chest")
        case 'levator scapulae' | 'traps':
            specificMuscles.add("upper back")
        case 'delts':
            specificMuscles.add("front shoulder")
        case 'abs':
            specificMuscles.add("abdominals")
        case 'lats' | 'spine':
            specificMuscles.add("middle back")
        case 'cardiovascular system' | _:
            specificMuscles.add("unspecified")
         
    exercise["specificMuscles"] = list(specificMuscles)
    if exercise["specificMuscles"]:
        exercise["specificMuscles"].sort()
    if len(exercise["specificMuscles"]) > 1 and "unspecified" in exercise["specificMuscles"]:
        exercise["specificMuscles"].remove("unspecified")
    del exercise['secondaryMuscles']
    del exercise['target']
    new_exercise_list.append(exercise)

equipment = set()
workout_category = set()
major_muscle_group = set()
specific_muscle_group = set()

for exercise in new_exercise_list:
    equipment.add(exercise["equipment"])
    workout_category.add(exercise["workoutCategory"])
    major_muscle_group.add(exercise["majorMuscle"])
    for specific_muscle in exercise["specificMuscles"]:
        specific_muscles.add(specific_muscle)

print(f"Equipment: {equipment}")
print()
print(f"workout category: {workout_category}")
print()
print(f"major muscle group: {major_muscle_group}")
print()
print(f"specific muscles: {specific_muscles}")
print()
    

with open("exercise_json/new_exercise_json.json", "w") as file:
    json.dump(new_exercise_list, file, indent=4)