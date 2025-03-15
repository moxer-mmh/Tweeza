"use client";

import { useState, useRef, useCallback } from "react";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Circle, Upload, X, FileText, File } from "lucide-react";

export default function Register() {
  const [step, setStep] = useState(1);
  const [userType, setUserType] = useState("");
  const [errors, setErrors] = useState({});
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    phoneNumber: "",
    email: "",
    password: "",
    confirmPassword: "",
    ssn: "",
    yearOfBirth: "",
    additionalInfo: "",
    acceptTerms: false,
    // Admin organization fields
    orgName: "",
    orgPhone: "",
    address: "",
    taxId: "",
    nonProfitId: "",
    yearEstablished: "",
    peopleServed: "",
    hasHealthPermit: false,
    documents: "",
  });

  // Update the state in the Register component to include file handling
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const fileInputRef = useRef(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleFileChange = useCallback((e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  }, []);

  const handleFiles = useCallback((files) => {
    const newFiles = Array.from(files).map((file) => ({
      id: Math.random().toString(36).substring(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      file: file,
    }));

    setUploadedFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const removeFile = useCallback((id) => {
    setUploadedFiles((prev) => prev.filter((file) => file.id !== id));
  }, []);

  const openFileDialog = useCallback(() => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  }, [fileInputRef]);

  // Get file icon based on file type
  const getFileIcon = useCallback((fileType) => {
    if (fileType.includes("pdf")) {
      return <File className="h-5 w-5 text-red-500" />;
    } else if (fileType.includes("image")) {
      return <File className="h-5 w-5 text-blue-500" />;
    } else if (fileType.includes("word") || fileType.includes("document")) {
      return <File className="h-5 w-5 text-indigo-500" />;
    } else if (fileType.includes("excel") || fileType.includes("sheet")) {
      return <File className="h-5 w-5 text-green-500" />;
    } else {
      return <FileText className="h-5 w-5 text-gray-500" />;
    }
  }, []);

  // Format file size
  const formatFileSize = useCallback((bytes) => {
    if (bytes < 1024) {
      return bytes + " bytes";
    } else if (bytes < 1024 * 1024) {
      return (bytes / 1024).toFixed(1) + " KB";
    } else {
      return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    }
  }, []);

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePhone = (phone) => {
    const phoneRegex = /^[0-9]{10}$/;
    return phoneRegex.test(phone);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear errors when user types
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }

    // Validate email
    if (name === "email" && value) {
      if (!validateEmail(value)) {
        setErrors((prev) => ({
          ...prev,
          email: "Please enter a valid email address",
        }));
      }
    }

    // Validate phone
    if (name === "phoneNumber" && value) {
      if (!validatePhone(value)) {
        setErrors((prev) => ({
          ...prev,
          phoneNumber: "Please enter a valid 10-digit phone number",
        }));
      }
    }

    // Validate password match
    if (name === "password" || name === "confirmPassword") {
      if (name === "password" && formData.confirmPassword) {
        // When password field changes, check against existing confirmPassword
        if (value !== formData.confirmPassword) {
          setErrors((prev) => ({
            ...prev,
            confirmPassword: "Passwords do not match",
          }));
        } else {
          setErrors((prev) => ({ ...prev, confirmPassword: "" }));
        }
      } else if (name === "confirmPassword") {
        // When confirmPassword field changes, check against password
        if (value !== formData.password) {
          setErrors((prev) => ({
            ...prev,
            confirmPassword: "Passwords do not match",
          }));
        } else {
          setErrors((prev) => ({ ...prev, confirmPassword: "" }));
        }
      }
    }
  };

  const handleCheckboxChange = (name, checked) => {
    setFormData((prev) => ({ ...prev, [name]: checked }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleUserTypeSelect = (type) => {
    setUserType(type);
    setStep(2);
  };

  const validateForm = () => {
    const newErrors = {};

    // Required fields validation
    if (!formData.firstName) newErrors.firstName = "First name is required";
    if (!formData.lastName) newErrors.lastName = "Last name is required";
    if (!formData.phoneNumber)
      newErrors.phoneNumber = "Phone number is required";
    if (!formData.email) newErrors.email = "Email is required";
    if (!formData.password) newErrors.password = "Password is required";
    if (!formData.confirmPassword)
      newErrors.confirmPassword = "Please confirm your password";

    // Email validation
    if (formData.email && !validateEmail(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    // Phone validation
    if (formData.phoneNumber && !validatePhone(formData.phoneNumber)) {
      newErrors.phoneNumber = "Please enter a valid 10-digit phone number";
    }

    // Password match validation
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    // Terms acceptance for volunteer
    if (userType === "volunteer" && !formData.acceptTerms) {
      newErrors.acceptTerms = "You must accept the terms and conditions";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNextStep = (e) => {
    e.preventDefault();
    // For admin registration, allow proceeding to step 3 after step 2
    if (userType === "admin" && step === 2) {
      setStep((prev) => prev + 1);
      return;
    }
    if (validateForm()) {
      setStep((prev) => prev + 1);
    }
  };

  const handlePrevStep = () => {
    setStep((prev) => prev - 1);
  };

  const handleSubmitRegistration = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    // For admin registration, check if files are uploaded
    if (userType === "admin" && step === 3 && uploadedFiles.length === 0) {
      setErrors((prev) => ({
        ...prev,
        documents: "Please upload required documents",
      }));
      return;
    }

    // Here you would typically handle the form submission to your backend
    console.log("Form submitted:", formData);
  };

  const renderFormFields = () => {
    if (userType === "traveler") {
      return (
        <form className="space-y-4" onSubmit={handleSubmitRegistration}>
          <div className="space-y-2">
            <label htmlFor="firstName" className="text-sm text-gray-600">
              First Name
            </label>
            <Input
              id="firstName"
              name="firstName"
              type="text"
              placeholder="Enter your first name"
              className={`border-gray-300 ${
                errors.firstName ? "border-red-500" : ""
              }`}
              value={formData.firstName}
              onChange={handleChange}
              required
            />
            {errors.firstName && (
              <p className="text-xs text-red-500 mt-1">{errors.firstName}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="lastName" className="text-sm text-gray-600">
              Last Name
            </label>
            <Input
              id="lastName"
              name="lastName"
              type="text"
              placeholder="Enter your last name"
              className={`border-gray-300 ${
                errors.lastName ? "border-red-500" : ""
              }`}
              value={formData.lastName}
              onChange={handleChange}
              required
            />
            {errors.lastName && (
              <p className="text-xs text-red-500 mt-1">{errors.lastName}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="phoneNumber" className="text-sm text-gray-600">
              Phone Number
            </label>
            <div className="flex gap-2">
              <Input
                id="phoneNumber"
                name="phoneNumber"
                type="tel"
                placeholder="Enter your phone number"
                className={`border-gray-300 ${
                  errors.phoneNumber ? "border-red-500" : ""
                }`}
                value={formData.phoneNumber}
                onChange={handleChange}
                required
              />
              <Button
                type="button"
                className="bg-red-700 hover:bg-red-800 text-white whitespace-nowrap"
              >
                Send Code
              </Button>
            </div>
            {errors.phoneNumber && (
              <p className="text-xs text-red-500 mt-1">{errors.phoneNumber}</p>
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
              placeholder="Enter password"
              className={`border-gray-300 ${
                errors.password ? "border-red-500" : ""
              }`}
              value={formData.password}
              onChange={handleChange}
              required
            />
            {errors.password && (
              <p className="text-xs text-red-500 mt-1">{errors.password}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="confirmPassword" className="text-sm text-gray-600">
              Confirm Password
            </label>
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              placeholder="Confirm password"
              className={`border-gray-300 ${
                errors.confirmPassword ? "border-red-500" : ""
              }`}
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
            {errors.confirmPassword && (
              <p className="text-xs text-red-500 mt-1">
                {errors.confirmPassword}
              </p>
            )}
          </div>

          <Button
            type="submit"
            className="w-full bg-red-700 hover:bg-red-800 text-white mt-4"
          >
            Continue
          </Button>

          <div className="text-center text-xs text-gray-500 mt-2">
            <span>Already have an account? </span>
            <Link href="/login" className="text-red-700">
              Login Now
            </Link>
          </div>
        </form>
      );
    }

    if (userType === "volunteer") {
      return (
        <form className="space-y-4" onSubmit={handleSubmitRegistration}>
          <div className="space-y-2">
            <label htmlFor="firstName" className="text-sm text-gray-600">
              First Name <span className="text-red-700">*</span>
            </label>
            <Input
              id="firstName"
              name="firstName"
              type="text"
              placeholder="Enter your first name"
              className={`border-gray-300 ${
                errors.firstName ? "border-red-500" : ""
              }`}
              value={formData.firstName}
              onChange={handleChange}
              required
            />
            {errors.firstName && (
              <p className="text-xs text-red-500 mt-1">{errors.firstName}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="lastName" className="text-sm text-gray-600">
              Last Name <span className="text-red-700">*</span>
            </label>
            <Input
              id="lastName"
              name="lastName"
              type="text"
              placeholder="Enter your last name"
              className={`border-gray-300 ${
                errors.lastName ? "border-red-500" : ""
              }`}
              value={formData.lastName}
              onChange={handleChange}
              required
            />
            {errors.lastName && (
              <p className="text-xs text-red-500 mt-1">{errors.lastName}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="phoneNumber" className="text-sm text-gray-600">
              Phone Number <span className="text-red-700">*</span>
            </label>
            <Input
              id="phoneNumber"
              name="phoneNumber"
              type="tel"
              placeholder="Enter your phone number"
              className={`border-gray-300 ${
                errors.phoneNumber ? "border-red-500" : ""
              }`}
              value={formData.phoneNumber}
              onChange={handleChange}
              required
            />
            {errors.phoneNumber && (
              <p className="text-xs text-red-500 mt-1">{errors.phoneNumber}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="email" className="text-sm text-gray-600">
              Email Address <span className="text-red-700">*</span>
            </label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="Enter your email address"
              className={`border-gray-300 ${
                errors.email ? "border-red-500" : ""
              }`}
              value={formData.email}
              onChange={handleChange}
              required
            />
            {errors.email && (
              <p className="text-xs text-red-500 mt-1">{errors.email}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="ssn" className="text-sm text-gray-600">
              Social Security Number <span className="text-red-700">*</span>
            </label>
            <Input
              id="ssn"
              name="ssn"
              type="text"
              placeholder="Enter your SSN"
              className={`border-gray-300 ${
                errors.ssn ? "border-red-500" : ""
              }`}
              value={formData.ssn}
              onChange={handleChange}
              required
            />
            {errors.ssn && (
              <p className="text-xs text-red-500 mt-1">{errors.ssn}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="yearOfBirth" className="text-sm text-gray-600">
              Year of Birth <span className="text-red-700">*</span>
            </label>
            <Input
              id="yearOfBirth"
              name="yearOfBirth"
              type="text"
              placeholder="YYYY"
              className={`border-gray-300 ${
                errors.yearOfBirth ? "border-red-500" : ""
              }`}
              value={formData.yearOfBirth}
              onChange={handleChange}
              required
            />
            {errors.yearOfBirth && (
              <p className="text-xs text-red-500 mt-1">{errors.yearOfBirth}</p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="additionalInfo" className="text-sm text-gray-600">
              Additional Information (Optional)
            </label>
            <Textarea
              id="additionalInfo"
              name="additionalInfo"
              placeholder="Enter any additional information"
              className="border-gray-300 resize-none h-24"
              value={formData.additionalInfo}
              onChange={handleChange}
            />
          </div>

          <div className="flex items-start space-x-2">
            <Checkbox
              id="acceptTerms"
              className={`mt-1 ${errors.acceptTerms ? "border-red-500" : ""}`}
              checked={formData.acceptTerms}
              onCheckedChange={(checked) =>
                handleCheckboxChange("acceptTerms", checked)
              }
            />
            <div>
              <label htmlFor="acceptTerms" className="text-xs text-gray-600">
                I accept the{" "}
                <Link href="/privacy" className="text-red-700">
                  Privacy Policy
                </Link>{" "}
                and{" "}
                <Link href="/terms" className="text-red-700">
                  Terms of Service
                </Link>
              </label>
              {errors.acceptTerms && (
                <p className="text-xs text-red-500 mt-1">
                  {errors.acceptTerms}
                </p>
              )}
            </div>
          </div>

          <Button
            type="submit"
            className="w-full bg-red-700 hover:bg-red-800 text-white mt-4"
          >
            Submit Registration
          </Button>

          <div className="text-center text-xs text-gray-500 mt-2">
            <span>Already have an account? </span>
            <Link href="/login" className="text-red-700">
              Login Now
            </Link>
          </div>
        </form>
      );
    }

    if (userType === "admin") {
      if (step === 2) {
        return (
          <form className="space-y-4" onSubmit={handleNextStep}>
            <div className="space-y-2">
              <label htmlFor="firstName" className="text-sm text-gray-600">
                First Name
              </label>
              <Input
                id="firstName"
                name="firstName"
                type="text"
                placeholder="Enter first name"
                className={`border-gray-300 ${
                  errors.firstName ? "border-red-500" : ""
                }`}
                value={formData.firstName}
                onChange={handleChange}
                required
              />
              {errors.firstName && (
                <p className="text-xs text-red-500 mt-1">{errors.firstName}</p>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="lastName" className="text-sm text-gray-600">
                Last Name
              </label>
              <Input
                id="lastName"
                name="lastName"
                type="text"
                placeholder="Enter last name"
                className={`border-gray-300 ${
                  errors.lastName ? "border-red-500" : ""
                }`}
                value={formData.lastName}
                onChange={handleChange}
                required
              />
              {errors.lastName && (
                <p className="text-xs text-red-500 mt-1">{errors.lastName}</p>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm text-gray-600">
                Email Address
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="Enter email address"
                className={`border-gray-300 ${
                  errors.email ? "border-red-500" : ""
                }`}
                value={formData.email}
                onChange={handleChange}
                required
              />
              {errors.email && (
                <p className="text-xs text-red-500 mt-1">{errors.email}</p>
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
                placeholder="Enter password"
                className={`border-gray-300 ${
                  errors.password ? "border-red-500" : ""
                }`}
                value={formData.password}
                onChange={handleChange}
                required
              />
              {errors.password && (
                <p className="text-xs text-red-500 mt-1">{errors.password}</p>
              )}
            </div>

            <div className="space-y-2">
              <label
                htmlFor="confirmPassword"
                className="text-sm text-gray-600"
              >
                Confirm Password
              </label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                placeholder="Confirm password"
                className={`border-gray-300 ${
                  errors.confirmPassword ? "border-red-500" : ""
                }`}
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
              {errors.confirmPassword && (
                <p className="text-xs text-red-500 mt-1">
                  {errors.confirmPassword}
                </p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full bg-red-700 hover:bg-red-800 text-white mt-4"
            >
              Continue
            </Button>

            <div className="text-center text-xs text-gray-500 mt-2">
              <span>Already have an account? </span>
              <Link href="/login" className="text-red-700">
                Login Now
              </Link>
            </div>
          </form>
        );
      }

      if (step === 3) {
        // Step 3: Organization verification form
        return (
          <form className="space-y-6" onSubmit={handleSubmitRegistration}>
            <div className="mb-6">
              <h2 className="text-xl font-medium text-gray-800">
                Organization Verification Details
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                Please provide information about your organization
              </p>
            </div>

            {/* Two-column layout for desktop */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="orgName" className="text-sm text-gray-600 flex">
                  Organization Name <span className="text-red-700 ml-1">*</span>
                </label>
                <Input
                  id="orgName"
                  name="orgName"
                  type="text"
                  placeholder="Enter organization name"
                  className={`border-gray-300 ${
                    errors.orgName ? "border-red-500" : ""
                  }`}
                  value={formData.orgName}
                  onChange={handleChange}
                  required
                />
                {errors.orgName && (
                  <p className="text-xs text-red-500 mt-1">{errors.orgName}</p>
                )}
              </div>

              <div className="space-y-2">
                <label
                  htmlFor="orgPhone"
                  className="text-sm text-gray-600 flex"
                >
                  Organization Phone{" "}
                  <span className="text-red-700 ml-1">*</span>
                </label>
                <Input
                  id="orgPhone"
                  name="orgPhone"
                  type="tel"
                  placeholder="Enter organization phone"
                  className={`border-gray-300 ${
                    errors.orgPhone ? "border-red-500" : ""
                  }`}
                  value={formData.orgPhone}
                  onChange={handleChange}
                  required
                />
                {errors.orgPhone && (
                  <p className="text-xs text-red-500 mt-1">{errors.orgPhone}</p>
                )}
              </div>

              <div className="space-y-2 md:col-span-2">
                <label htmlFor="address" className="text-sm text-gray-600 flex">
                  Complete Address <span className="text-red-700 ml-1">*</span>
                </label>
                <Input
                  id="address"
                  name="address"
                  type="text"
                  placeholder="Enter complete address"
                  className={`border-gray-300 ${
                    errors.address ? "border-red-500" : ""
                  }`}
                  value={formData.address}
                  onChange={handleChange}
                  required
                />
                {errors.address && (
                  <p className="text-xs text-red-500 mt-1">{errors.address}</p>
                )}
              </div>

              <div className="space-y-2">
                <label htmlFor="taxId" className="text-sm text-gray-600 flex">
                  Tax ID Number <span className="text-red-700 ml-1">*</span>
                </label>
                <Input
                  id="taxId"
                  name="taxId"
                  type="text"
                  placeholder="Enter Tax ID"
                  className={`border-gray-300 ${
                    errors.taxId ? "border-red-500" : ""
                  }`}
                  value={formData.taxId}
                  onChange={handleChange}
                  required
                />
                {errors.taxId && (
                  <p className="text-xs text-red-500 mt-1">{errors.taxId}</p>
                )}
              </div>

              <div className="space-y-2">
                <label
                  htmlFor="nonProfitId"
                  className="text-sm text-gray-600 flex"
                >
                  Non-Profit Registration Number{" "}
                  <span className="text-red-700 ml-1">*</span>
                </label>
                <Input
                  id="nonProfitId"
                  name="nonProfitId"
                  type="text"
                  placeholder="Enter registration number"
                  className={`border-gray-300 ${
                    errors.nonProfitId ? "border-red-500" : ""
                  }`}
                  value={formData.nonProfitId}
                  onChange={handleChange}
                  required
                />
                {errors.nonProfitId && (
                  <p className="text-xs text-red-500 mt-1">
                    {errors.nonProfitId}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label
                  htmlFor="yearEstablished"
                  className="text-sm text-gray-600 flex"
                >
                  Year Established <span className="text-red-700 ml-1">*</span>
                </label>
                <Input
                  id="yearEstablished"
                  name="yearEstablished"
                  type="text"
                  placeholder="Enter year"
                  className={`border-gray-300 ${
                    errors.yearEstablished ? "border-red-500" : ""
                  }`}
                  value={formData.yearEstablished}
                  onChange={handleChange}
                  required
                />
                {errors.yearEstablished && (
                  <p className="text-xs text-red-500 mt-1">
                    {errors.yearEstablished}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label
                  htmlFor="peopleServed"
                  className="text-sm text-gray-600 flex"
                >
                  Monthly People Served{" "}
                  <span className="text-red-700 ml-1">*</span>
                </label>
                <Input
                  id="peopleServed"
                  name="peopleServed"
                  type="text"
                  placeholder="Enter number of people"
                  className={`border-gray-300 ${
                    errors.peopleServed ? "border-red-500" : ""
                  }`}
                  value={formData.peopleServed}
                  onChange={handleChange}
                  required
                />
                {errors.peopleServed && (
                  <p className="text-xs text-red-500 mt-1">
                    {errors.peopleServed}
                  </p>
                )}
              </div>

              <div className="space-y-2 md:col-span-2">
                <label className="text-sm text-gray-600">
                  Health Department Permit
                </label>
                <div className="flex items-start space-x-2">
                  <Checkbox
                    id="healthPermit"
                    className="mt-1"
                    checked={formData.hasHealthPermit}
                    onCheckedChange={(checked) =>
                      handleCheckboxChange("hasHealthPermit", checked)
                    }
                  />
                  <label
                    htmlFor="healthPermit"
                    className="text-xs text-gray-600"
                  >
                    We have a valid health department permit
                  </label>
                </div>
              </div>
            </div>

            {/* Document upload section*/}
            <div className="space-y-4 mt-8">
              <div className="flex items-center justify-between">
                <label
                  htmlFor="documents"
                  className="text-sm font-medium text-gray-700 flex items-center"
                >
                  Required Documents{" "}
                  <span className="text-red-700 ml-1">*</span>
                </label>
                {uploadedFiles.length > 0 && (
                  <span className="text-xs text-gray-500">
                    {uploadedFiles.length} file(s) selected
                  </span>
                )}
              </div>

              <div
                className={`border-2 border-dashed rounded-md p-8 transition-colors ${
                  dragActive
                    ? "border-red-500 bg-red-50"
                    : "border-gray-300 hover:border-red-700"
                } cursor-pointer`}
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={openFileDialog}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  id="fileInput"
                  multiple
                  className="hidden"
                  onChange={handleFileChange}
                />
                <div className="flex flex-col items-center justify-center text-center">
                  <Upload className="h-12 w-12 text-red-700 mb-3" />
                  <p className="text-base font-medium text-gray-700">
                    Drag and drop your documents here
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    or click to browse your files
                  </p>
                  <p className="text-xs text-gray-400 mt-3 max-w-md mx-auto">
                    Upload Health Tax Exemption Certificate, Health Permit,
                    Non-Profit registration, and any other relevant
                    documentation
                  </p>
                </div>
              </div>
              {errors.documents && (
                <p className="text-xs text-red-500">{errors.documents}</p>
              )}

              {/* Display uploaded files in a grid for desktop */}
              {uploadedFiles.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-medium text-gray-700 mb-3">
                    Uploaded Documents
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {uploadedFiles.map((file) => (
                      <div
                        key={file.id}
                        className="flex items-center justify-between bg-gray-50 p-3 rounded-md border border-gray-200 hover:border-red-200 transition-colors"
                      >
                        <div className="flex items-center overflow-hidden">
                          {getFileIcon(file.type)}
                          <div className="ml-3 overflow-hidden">
                            <p className="text-sm font-medium text-gray-700 truncate max-w-[150px]">
                              {file.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {formatFileSize(file.size)}
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            removeFile(file.id);
                          }}
                          className="text-gray-400 hover:text-red-700 transition-colors ml-2 p-1 rounded-full hover:bg-red-50"
                          aria-label="Remove file"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex flex-col md:flex-row gap-3 pt-6">
              <Button
                type="button"
                variant="outline"
                className="w-full md:w-auto border-gray-300"
                onClick={handlePrevStep}
              >
                Back to Step 2
              </Button>

              <Button
                type="submit"
                className="w-full md:w-auto bg-red-700 hover:bg-red-800 text-white"
              >
                Submit Registration
              </Button>

              <div className="text-center md:text-right text-xs text-gray-500 mt-2 md:mt-0 md:ml-auto md:self-center">
                <span>Already have an account? </span>
                <Link href="/login" className="text-red-700">
                  Login Now
                </Link>
              </div>
            </div>
          </form>
        );
      }
    }

    return null;
  };

  // Fix the return statement to always show step indicator after role selection
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <div className="w-full max-w-md md:max-w-2xl border border-gray-200 rounded-md p-6 md:p-8">
        <div className="flex border-b mb-6">
          <Link
            href="/login"
            className="text-sm font-medium pb-2 px-4 text-gray-600"
          >
            Login
          </Link>
          <div className="text-sm font-medium pb-2 px-4 text-red-700 border-b-2 border-red-700">
            Register
          </div>
        </div>

        {/* Step 1: User Type Selection */}
        {step === 1 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Admin Option */}
            <div
              className="border rounded-md p-4 hover:border-red-700 cursor-pointer transition-colors hover:shadow-sm"
              onClick={() => handleUserTypeSelect("admin")}
            >
              <div className="flex items-start gap-3">
                <div className="bg-red-700 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm flex-shrink-0">
                  A
                </div>
                <div>
                  <h3 className="font-medium text-sm">Admin</h3>
                  <p className="text-xs text-gray-500 mt-1">
                    Register as an administrator to manage the platform
                  </p>
                </div>
              </div>
            </div>

            {/* Traveler Option */}
            <div
              className="border rounded-md p-4 hover:border-red-700 cursor-pointer transition-colors hover:shadow-sm"
              onClick={() => handleUserTypeSelect("traveler")}
            >
              <div className="flex items-start gap-3">
                <div className="bg-red-700 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm flex-shrink-0">
                  T
                </div>
                <div>
                  <h3 className="font-medium text-sm">Traveler</h3>
                  <p className="text-xs text-gray-500 mt-1">
                    Register as a traveler to book and explore
                  </p>
                </div>
              </div>
            </div>

            {/* Volunteer Option */}
            <div
              className="border rounded-md p-4 hover:border-red-700 cursor-pointer transition-colors hover:shadow-sm"
              onClick={() => handleUserTypeSelect("volunteer")}
            >
              <div className="flex items-start gap-3">
                <div className="bg-red-700 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm flex-shrink-0">
                  V
                </div>
                <div>
                  <h3 className="font-medium text-sm">Volunteer</h3>
                  <p className="text-xs text-gray-500 mt-1">
                    Register as a volunteer to help and contribute
                  </p>
                </div>
              </div>
            </div>

            <div className="text-center text-xs text-gray-500 mt-4 md:col-span-3">
              <span>Already have an account? </span>
              <Link href="/login" className="text-red-700">
                Login Now
              </Link>
            </div>
          </div>
        )}

        {step > 1 && renderFormFields()}
      </div>
    </div>
  );
}
