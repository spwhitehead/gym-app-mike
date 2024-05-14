"use client";
// src/app/exercises/page.tsx
import { useEffect, useState } from "react";
import Layout from "../../../components/Layout";
import { fetchExercises } from "../../../utils/api";
import ExerciseCard from "../../../components/ExerciseCard";

interface Exercise {
  uuid: string;
  name: string;
  description: string;
  workout_category: string;
  movement_category: string;
  equipment: string;
  major_muscle: string;
  specific_muscles: string[];
}

const Exercises: React.FC = () => {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [error, setError] = useState<string | null>(null);

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
      <h2 className="text-2xl">Exercises</h2>
      {error && <p className="text-red-500">{error}</p>}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {exercises.map((exercise) => (
          <ExerciseCard key={exercise.uuid} {...exercise} />
        ))}
      </div>
    </Layout>
  );
};

export default Exercises;
