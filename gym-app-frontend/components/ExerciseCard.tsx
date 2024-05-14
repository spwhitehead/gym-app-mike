"use client;";
import "../src/app/styles/globals.css";
export default function ExerciseCard({
  name,
  description,
  workout_category,
  movement_category,
  equipment,
  major_muscle,
  specific_muscles,
}: {
  name: string;
  description: string;
  workout_category: string;
  movement_category: string;
  equipment: string;
  major_muscle: string;
  specific_muscles: string[];
}) {
  return (
    <div className="bg-gradient-to-r from-green-400 to-blue-500 shadow-lg rounded-lg p-6 mb-4 text-white">
      <h3 className="text-2xl font-bold mb-2">{name}</h3>
      <p className="text-gray-100 mb-4">{description}</p>
      <div className="mb-4">
        <strong>Workout Category: </strong>
        {workout_category}
      </div>
      <div className="mb-4">
        <strong>Movement Category: </strong>
        {movement_category}
      </div>
      <div className="mb-4">
        <strong>Equipment: </strong>
        {equipment}
      </div>
      <div className="mb-4">
        <strong>Major Muscle: </strong>
        {major_muscle}
      </div>
      <div className="mb-4">
        <strong>Specific Muscles: </strong>
        {specific_muscles.join(", ")}
      </div>
    </div>
  );
}
