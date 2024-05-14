// src/app/login/page.tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Layout from "../../../components/Layout";
import { login } from "../../../utils/api";

const Login: React.FC = () => {
  const router = useRouter();
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [errorDescription, setErrorDescription] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await login(formData.username, formData.password);
      localStorage.setItem("token", response.access_token);
      router.push("/exercises");
    } catch (err: any) {
      setError("Login failed");
      setErrorDescription(err.detail);
      console.log(err);
    }
  };

  return (
    <Layout>
      <h2 className="text-2xl">Login</h2>
      <form onSubmit={handleSubmit} className="flex flex-col items-center py-4 w-full max-w-md mx-auto">
        <div className="flex flex-col w-full mb-3">
          <label htmlFor="username" className="mb-1 text-left">
            Username:
          </label>
          <input
            type="text"
            id="username"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            className="p-2 border w-full"
            required
          />
        </div>
        <div className="flex flex-col w-full mb-3">
          <label htmlFor="password" className="mb-1 text-left">
            Password:
          </label>
          <input
            type="password"
            id="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            className="p-2 border w-full"
            required
          />
        </div>
        <button type="submit" className="p-2 bg-blue-500 text-white w-full">
          Login
        </button>
        {error && <p className="text-red-500 text-center mt-2">{error}</p>}
        {errorDescription && <p className="text-red-500 text-center mt-2">{errorDescription}</p>}
      </form>
    </Layout>
  );
};

export default Login;
