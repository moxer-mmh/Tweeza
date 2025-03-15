"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

export default function AssistancePage() {
  const { id } = useParams();
  const [assistance, setAssistance] = useState(null);
  const [services, setServices] = useState([]);

  useEffect(() => {
    const mockAssistance = {
      id: parseInt(id),
      title: "Legal Aid Services",
      location: "Community Center",
      date: "2024-04-15",
      time: "10:00 AM - 4:00 PM",
      description:
        "Free legal consultation services for community members. Our volunteer attorneys provide guidance on various legal matters including housing, employment, and family law.",
      services: [
        { id: 1, name: "Housing Rights Consultation", available: true },
        { id: 2, name: "Employment Law Advice", available: true },
        { id: 3, name: "Family Law Guidance", available: true },
        { id: 4, name: "Immigration Consultation", available: false },
      ],
      eligibility: [
        "Open to all community members",
        "Priority given to low-income individuals",
        "Bring identification and relevant documents",
      ],
    };

    setAssistance(mockAssistance);
    setServices(mockAssistance.services);
  }, [id]);

  if (!assistance) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container max-w-md mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link href="/" className="text-gray-600 hover:text-gray-800">
          <ChevronLeft className="h-6 w-6" />
        </Link>
        <h1 className="text-[18px] font-semibold">Assistance Services</h1>
      </div>
      <div className="border border-[#E8E8E8] p-4 rounded-[16px] shadow-md bg-white">
        {/* Location and Time */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <span className="font-semibold text-[16px]">
                {assistance.location}
              </span>
            </div>
            <div className="flex items-center">
              <span className="text-sm text-gray-500 mr-1">•</span>
              <span className="text-sm text-gray-500">
                {new Date(assistance.date).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        {/* Description */}
        <div className="mb-4">
          <h2 className="text-xs font-medium text-gray-700 uppercase mb-2">
            ABOUT THIS SERVICE
          </h2>
          <p className="text-sm text-gray-600">{assistance.description}</p>
        </div>

        {/* Services Available */}
        <div className="space-y-3 mb-4">
          <h2 className="text-xs font-medium text-gray-700 uppercase">
            AVAILABLE SERVICES
          </h2>
          {services.map((service) => (
            <div
              key={service.id}
              className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200"
            >
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm">{service.name}</span>
                {service.available ? (
                  <span className="px-2 py-0.5 text-xs font-medium text-blue-700 bg-blue-50 rounded-full">
                    Available
                  </span>
                ) : (
                  <span className="px-2 py-0.5 text-xs font-medium text-gray-700 bg-gray-100 rounded-full">
                    Unavailable
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Eligibility Requirements */}
        <div className="mb-4">
          <h2 className="text-xs font-medium text-gray-700 uppercase mb-2">
            ELIGIBILITY & REQUIREMENTS
          </h2>
          <ul className="text-sm text-gray-600 space-y-2 list-disc pl-5">
            {assistance.eligibility.map((req, index) => (
              <li key={index}>{req}</li>
            ))}
          </ul>
        </div>

        {/* Appointment Time */}
        <div className="mb-4">
          <h2 className="text-xs font-medium text-gray-700 uppercase mb-2">
            SELECT APPOINTMENT TIME
          </h2>
          <div className="relative">
            <select className="w-full p-3 bg-white border border-gray-200 rounded-lg text-gray-700 appearance-none pr-8">
              <option>Today, 10:00 AM - 11:00 AM</option>
              <option>Today, 11:00 AM - 12:00 PM</option>
              <option>Today, 1:00 PM - 2:00 PM</option>
              <option>Today, 2:00 PM - 3:00 PM</option>
              <option>Today, 3:00 PM - 4:00 PM</option>
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <svg
                className="w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M19 9l-7 7-7-7"
                ></path>
              </svg>
            </div>
          </div>
        </div>

        {/* Location */}
        <div className="mb-6">
          <div className="flex items-center">
            <svg
              className="w-5 h-5 mr-1 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
              ></path>
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
              ></path>
            </svg>
            <span className="text-xs font-medium text-gray-700">
              {assistance.location}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col gap-2">
          <Button
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg"
            onClick={() =>
              console.log("Request assistance", {
                assistanceId: id,
                service: services.find((s) => s.available),
              })
            }
          >
            Request Assistance
          </Button>
          <Link href="/" className="w-full text-center">
            <button className="w-full text-gray-700 py-2 px-4">Cancel</button>
          </Link>
        </div>
      </div>
    </div>
  );
}
