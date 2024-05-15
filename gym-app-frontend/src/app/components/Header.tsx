import "@/app/styles/globals.css";
import Link from "next/link";
import { useAuth } from "./AuthContext";

export default function Header() {
  const { token, setToken } = useAuth();

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };
  return (
    <header className="bg-blue-500 text-white p-4 fixed top-0 w-full z-50">
      <h1 className="text-xl">Gym App</h1>
      <nav className="w-full">
        <Link href="/">Home</Link> |{" "}
        {token ? (
          <>
            {" "}
            <Link onClick={handleLogout} href="/login">
              Logout
            </Link>{" "}
            | <Link href="/exercises">Exercises</Link> | <Link href="/workouts">Workouts</Link>{" "}
          </>
        ) : (
          <>
            {" "}
            <Link href="/register">Register</Link> | <Link href="/login">Login</Link>{" "}
          </>
        )}
      </nav>
    </header>
  );
}
