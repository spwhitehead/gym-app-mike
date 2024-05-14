"use client";
import "../app/globals.css";
import { useRouter } from "next/router";
export default function Register() {
  const baseURL = "http://localhost:8000";
  const router = useRouter();

  function handleRegister(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget as HTMLFormElement;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    fetch(baseURL + "/users/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        if (data.data) {
          alert("Successfully registered! " + "\n" + data.data.username + "\n" + data.detail);
          form.reset();
          router.push("/login");
        } else {
          alert("Failed to register: " + data.detail);
        }
      })
      .catch((error) => {
        console.error("Failed to register:", error);
      });
  }
  return (
    <div>
      <h1>Register</h1>
      <p>Please register below!</p>
      <form onSubmit={handleRegister}>
        <ul id="register_form" className="register-form">
          <li>
            <label>
              Username:
              <input type="text" name="username" required />
            </label>
          </li>
          <li>
            <label>
              Password:
              <input type="password" name="hashed_password" required />
            </label>
          </li>
          <li>
            <label>
              Birthday:
              <input type="date" name="birthday" required />
            </label>
          </li>
          <li>
            <label>
              First Name:
              <input type="text" name="first_name" required />
            </label>
          </li>
          <li>
            <label>
              Last Name:
              <input type="text" name="last_name" required />
            </label>
          </li>
          <li>
            <label>
              Body Weight:
              <input type="number" name="body_weight" step="1" required />
            </label>
          </li>
          <li>
            <label>
              Height (inches):
              <input type="number" name="height" step="1" required />
            </label>
          </li>
          <li>
            <label id="gender">
              Gender:
              <select name="gender">
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </label>
          </li>
        </ul>
        <button type="submit"> Register </button>
      </form>
    </div>
  );
}
