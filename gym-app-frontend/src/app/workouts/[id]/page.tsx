// src/app/workouts/[id]/page.tsx
"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Layout from "../../components/Layout";
import { fetchWorkoutById } from "../../utils/api";

interface Workout {
  id: number;
  name: string;
  description: string;
}

const WorkoutDetail: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const [workout, setWorkout] = useState<Workout | null>(null);

  useEffect(() => {
    if (id) {
      fetchWorkoutById(id as string)
        .then(setWorkout)
        .catch(console.error);
    }
  }, [id]);

  if (!workout) {
    return <Layout>Loading...</Layout>;
  }

  return (
    <Layout>
      <h2 className="text-2xl">{workout.name}</h2>
      <p>{workout.description}</p>
    </Layout>
  );
};

export default WorkoutDetail;
