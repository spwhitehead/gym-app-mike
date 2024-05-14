// src/app/workouts/page.tsx
"use client";
import { useEffect, useState } from "react";
import Layout from "../../../components/Layout";
import { fetchWorkouts } from "../../../utils/api";

interface Workout {
  uuid: string;
  name: string;
}

const Workouts: React.FC = () => {
  const [workouts, setWorkouts] = useState<Workout[]>([]);

  useEffect(() => {
    fetchWorkouts().then(setWorkouts).catch(console.error);
  }, []);

  return (
    <Layout>
      <h2 className="text-2xl">Workouts</h2>
      <ul>
        {workouts.map((workout) => (
          <li key={workout.uuid} className="py-2">
            {workout.name}
          </li>
        ))}
      </ul>
    </Layout>
  );
};

export default Workouts;
