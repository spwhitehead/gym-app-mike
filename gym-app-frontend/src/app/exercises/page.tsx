"use client";
// src/app/exercises/page.tsx
import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { fetchExercises } from "../utils/api";
import ExerciseCard from "../components/ExerciseCard";

interface Exercise {
  uuid: string;
  name: string;
  description: string;
  workout_category: string;
  movement_category: string;
  equipment: string;
  major_muscle: string;
  specific_muscles: string[];
  image_url: string;
}

const Exercises: React.FC = () => {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const handleToggle = (id: string) => {
    setExpandedId((prevId) => (prevId === id ? null : id));
  };

  useEffect(() => {
    const getExercises = async () => {
      try {
        const response = await fetchExercises();
        setExercises(response.data);
      } catch (err) {
        setError("Failed to fetch exercises");
        console.error(err);
      }
    };

    getExercises();
  }, []);

  return (
    <Layout>
      <h2 className="text-2xl mb-10 text-center">Exercises</h2>
      {error && <p className="text-red-500">{error}</p>}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {exercises.map((exercise) => (
          <ExerciseCard key={exercise.uuid} isExpanded={expandedId === exercise.uuid} onToggle={() => handleToggle(exercise.uuid)} {...exercise} />
        ))}
      </div>
    </Layout>
  );
};

export default Exercises;
