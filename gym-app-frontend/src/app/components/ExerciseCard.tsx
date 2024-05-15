"use client;";
import Image from "next/image";
import "@/app/styles/globals.css";
import { useState } from "react";
export default function ExerciseCard({
  name,
  description,
  workout_category,
  movement_category,
  equipment,
  major_muscle,
  specific_muscles,
  image_url,
  isExpanded,
  onToggle,
}: {
  name: string;
  description: string;
  workout_category: string;
  movement_category: string;
  equipment: string;
  major_muscle: string;
  specific_muscles: string[];
  image_url: string;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const [showDescription, setShowDescription] = useState(false);

  function toggleDescription() {
    setShowDescription((prev) => !prev);
  }

  return (
    <div
      className={`bg-gradient-to-br from-gray-800 to-gray-900 hover:bg-gradient-to-br hover:from-gray-700 hover:to-gray-900 shadow-xl rounded-lg p-6 mb-6 mx-2 text-white cursor-pointer transform transition-all hover:scale-105  ${
        isExpanded ? "transition" : "h-24 overflow-hidden"
      } ${isExpanded ? "transition" : "transition"}`}
    >
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold w-2/3" onClick={onToggle}>
          {name}
        </h3>
        <span className="text-sm w-1/3 text-right" onClick={onToggle}>
          {isExpanded ? "Hide Details" : "Show Details"}
        </span>
      </div>
      {isExpanded && (
        <div className="mt-4">
          <div className="space-y-4 mx-5 mb-10">
            {image_url && (
              <div className="flex justify-center h-full">
                <Image src={image_url} alt={name} width={200} height={200} className="rounded-2xl" unoptimized></Image>
              </div>
            )}
            <div className="flex justify-between items-center p-2 bg-gray-700 rounded-md transition-transform hover:scale-105 hover:text-gray-700 hover:bg-gray-100 hover:font-bold">
              <strong className="text-sm">Workout Category: </strong>
              <span className="text-sm">{workout_category}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-700 rounded-md transition-transform hover:scale-105 hover:text-gray-700 hover:bg-gray-100 hover:font-bold">
              <strong className="text-sm">Movement Category: </strong>
              <span className="text-sm">{movement_category}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-700 rounded-md transition-transform hover:scale-105 hover:text-gray-700 hover:bg-gray-100 hover:font-bold">
              <strong className="text-sm">Equipment: </strong>
              <span className="text-sm">{equipment}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-700 rounded-md transition-transform hover:scale-105 hover:text-gray-700 hover:bg-gray-100 hover:font-bold">
              <strong className="text-sm">Major Muscle: </strong>
              <span className="text-sm">{major_muscle}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-700 rounded-md transition-transform hover:scale-105 hover:text-gray-700 hover:bg-gray-100 hover:font-bold">
              <strong className="text-sm">Specific Muscles: </strong>
              <span className="text-sm">{specific_muscles.join(", ")}</span>
            </div>
          </div>
          <div className="mx-5">
            <p className="mb-5 cursor-pointer text-sm" onClick={toggleDescription}>
              {showDescription ? "Hide Description" : "Show Description"}
            </p>
            {showDescription && <p className="text-gray-300 mb-4 p-4 bg-gray-800 rounded-lg transition-transform hover:scale-105">{description}</p>}
          </div>
        </div>
      )}
    </div>
  );
}
