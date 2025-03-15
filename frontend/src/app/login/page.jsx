"use client";

import { useState } from "react";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function Login() {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    emailPhone: "",
    password: "",
  });
  const [errors, setErrors] = useState({});

  const validateEmailPhone = (value) => {
    // Email validation regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    // Phone number validation regex (basic format)
    const phoneRegex = /^[0-9]{10}$/;

    if (!value) {
      return "This field is required";
    }
    if (!emailRegex.test(value) && !phoneRegex.test(value)) {
      return "Please enter a valid email or phone number";
    }
    return "";
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear errors when user types
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }

    // Validate email/phone as user types
    if (name === "emailPhone") {
      const error = validateEmailPhone(value);
      if (error) {
        setErrors((prev) => ({ ...prev, emailPhone: error }));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    // Validate all fields
    const newErrors = {
      emailPhone: validateEmailPhone(formData.emailPhone),
      password: !formData.password ? "Password is required" : "",
    };

    setErrors(newErrors);

    // Check if there are any errors
    if (Object.values(newErrors).some((error) => error)) {
      setIsLoading(false);
      return;
    }

    try {
      // TODO: Implement actual login logic here
      await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulated API call
      // Handle successful login (e.g., redirect to dashboard)
    } catch (error) {
      setErrors((prev) => ({
        ...prev,
        submit: "Failed to login. Please try again.",
      }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <div className="w-full max-w-md border border-gray-200 rounded-md p-6">
        <div className="flex border-b mb-6">
          <div className="text-sm font-medium pb-2 px-4 text-red-700 border-b-2 border-red-700">
            Login
          </div>
          <Link
            href="/register"
            className="text-sm font-medium pb-2 px-4 text-gray-600"
          >
            Register
          </Link>
        </div>

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label htmlFor="emailPhone" className="text-sm text-gray-600">
              Email/Phone
            </label>
            <Input
              id="emailPhone"
              name="emailPhone"
              type="text"
              placeholder="Enter your email or phone"
              className={`border-gray-300 ${
                errors.emailPhone ? "border-red-500" : ""
              }`}
              value={formData.emailPhone}
              onChange={handleChange}
              disabled={isLoading}
            />
            {errors.emailPhone && (
              <p className="text-xs text-red-500 mt-1">{errors.emailPhone}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm text-gray-600">
              Password
            </label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder="Enter your password"
              className={`border-gray-300 ${
                errors.password ? "border-red-500" : ""
              }`}
              value={formData.password}
              onChange={handleChange}
              disabled={isLoading}
            />
            {errors.password && (
              <p className="text-xs text-red-500 mt-1">{errors.password}</p>
            )}
          </div>

          <div className="flex justify-end">
            <Link href="/forgot-password" className="text-xs text-red-700">
              Forgot Password?
            </Link>
          </div>

          {errors.submit && (
            <p className="text-xs text-red-500 text-center">{errors.submit}</p>
          )}

          <Button
            type="submit"
            className="w-full bg-red-700 hover:bg-red-800 text-white"
            disabled={isLoading}
          >
            {isLoading ? "Logging in..." : "Login"}
          </Button>

          <div className="text-center text-xs text-gray-500 mt-4">
            <span>Don't have an account? </span>
            <Link href="/register" className="text-red-700">
              Register Now
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
