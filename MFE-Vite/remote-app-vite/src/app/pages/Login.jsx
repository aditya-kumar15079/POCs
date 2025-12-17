import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginApi } from "../services/api";

export default function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear field-level error while typing
    setErrors((prev) => ({
      ...prev,
      [name]: "",
    }));
  };

  const validate = () => {
    const newErrors = {};

    if (!form.username.trim()) {
      newErrors.username = "Username is required";
    }

    if (!form.password) {
      newErrors.password = "Password is required";
    } else if (form.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const login = async (e) => {
    e.preventDefault();

    if (!validate()) return;

    // const response = await loginApi(form);
    // if (response?.token?.access_token) {
    //   sessionStorage.setItem("authToken", response.token.access_token);
    //   navigate("/home");
    //   return;
    // }
    navigate("/home");
  };

  return (
    <div className="flex items-center justify-center h-screen bg-bg">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full md:w-lg">
        <h2 className="text-2xl font-bold mb-2 text-center">Login</h2>
        <form onSubmit={login} className="max-w-sm mx-auto">
          <div className="mb-4">
            <label className="block text-sm font-bold mb-2" htmlFor="username">
              Username
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={form.username}
              onChange={handleChange}
              className="w-full bg-gray-50 rounded-lg px-2 py-3 outline-none border border-gray-300"
              placeholder="Enter your username"
            />
            {errors.username && <p className="text-red-500 text-xs mt-1">{errors.username}</p>}
          </div>

          <div className="mb-6">
            <label className="block text-sm font-bold mb-2" htmlFor="password">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              className="w-full bg-gray-50 rounded-lg px-2 py-3 outline-none border border-gray-300"
              placeholder="Enter your password"
            />
            {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
          </div>

          <button type="submit" className="primary-button w-full">
            Login
          </button>
        </form>
      </div>
    </div>
  );
}
