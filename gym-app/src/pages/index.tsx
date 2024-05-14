"use client";
import "../app/globals.css";
import "../styles/index.css";
import { useState } from "react";
import { useRouter } from "next/router";

export default function Login() {
  const baseURL = "http://localhost:8000";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  const handleRegister = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    // Assuming your API endpoint for register is 'http://localhost:8000/users/register'
    router.push("/register");
  };

  const handleLogin = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // Assuming your API endpoint for login is 'http://localhost:8000/users/login'
    const response = await fetch(baseURL + "/users/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("token", data.token); // store the token
      router.push("/dashboard"); // navigate to dashboard
    } else {
      console.error("Failed to login:", data.message); // handle errors
    }
  };

  return (
    <>
      <form onSubmit={handleLogin}>
        <label>
          Username:
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        <label>
          Password:
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <button type="submit">Login</button>
      </form>
      <button id="register_button" type="button" onClick={handleRegister}>
        Register
      </button>
    </>
  );
}
