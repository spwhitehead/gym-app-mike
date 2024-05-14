import "../src/app/styles/globals.css";
import Link from "next/link";

export default function Header() {
  return (
    <header className="bg-blue-500 text-white p-4">
      <h1 className="text-xl">Gym App</h1>
      <nav>
        <Link href="/">Home</Link> | <Link href="/register">Register</Link> | <Link href="/login">Login</Link> |{" "}
        <Link href="/exercises">Exercises</Link> | <Link href="/workouts">Workouts</Link>
      </nav>
    </header>
  );
}
