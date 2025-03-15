"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ChevronLeft } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

export default function VolunteerPage() {
  const { id } = useParams();
  const [opportunity, setOpportunity] = useState(null);
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const mockOpportunity = {
      id: parseInt(id),
      title: "Food Distribution Center",
      location: "City Park",
      date: "2024-04-01",
      time: "9:00 AM - 12:00 PM",
      description:
        "Help us distribute food packages for families in need. We need volunteers to sort, package, and hand out food items to community members.",
      tasks: [
        { id: 1, name: "Sort and organize donated items", checked: false },
        { id: 2, name: "Pack boxes with food and supplies", checked: false },
        { id: 3, name: "Help load packages into vehicles", checked: false },
        {
          id: 4,
          name: "Track inventory and maintain database",
          checked: false,
        },
      ],
      requirements: [
        "Must be at least 18 years old",
        "Able to lift up to 25 pounds",
        "Valid photo ID for verification",
      ],
    };

    setOpportunity(mockOpportunity);
    setTasks(mockOpportunity.tasks);
  }, [id]);

  const handleTaskToggle = (taskId, checked) => {
    setTasks(
      tasks.map((task) => {
        if (task.id === taskId) {
          return { ...task, checked };
        }
        return task;
      })
    );
  };

  if (!opportunity) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container max-w-md mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link href="/" className="text-gray-600 hover:text-gray-800">
          <ChevronLeft className="h-6 w-6" />
        </Link>
        <h1 className="text-[18px] font-semibold">Volunteer Opportunity</h1>
      </div>
      <div className="border border-[#E8E8E8] p-4 rounded-[16px] shadow-md bg-white">
        {/* Location and Time */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <span className="font-semibold text-[16px]">
                {opportunity.location}
              </span>
            </div>
            <div className="flex items-center">
              <span className="text-sm text-gray-500 mr-1">•</span>
              <span className="text-sm text-gray-500">
                {new Date(opportunity.date).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        {/* Description */}
        <div className="mb-4">
          <h2 className="text-xs font-medium text-gray-700 uppercase mb-2">
            WHAT YOU'LL DO
          </h2>
          <p className="text-sm text-gray-600">{opportunity.description}</p>
        </div>

        {/* Tasks Selection */}
        <div className="space-y-3 mb-4">
          <h2 className="text-xs font-medium text-gray-700 uppercase">TASKS</h2>
          {tasks.map((task) => (
            <div
              key={task.id}
              className="flex items-start gap-3 p-3 bg-white rounded-lg border border-gray-200"
            >
              <Checkbox
                id={`task-${task.id}`}
                checked={task.checked}
                onCheckedChange={(checked) =>
                  handleTaskToggle(task.id, checked)
                }
                className="mt-0.5"
              />
              <label
                htmlFor={`task-${task.id}`}
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                {task.name}
              </label>
            </div>
          ))}
        </div>

        {/* Experience & Requirements */}
        <div className="mb-4">
          <h2 className="text-xs font-medium text-gray-700 uppercase mb-2">
            EXPERIENCE & REQUIREMENTS
          </h2>
          <ul className="text-sm text-gray-600 space-y-2 list-disc pl-5">
            {opportunity.requirements.map((req, index) => (
              <li key={index}>{req}</li>
            ))}
          </ul>
        </div>

        {/* Availability Time */}
        <div className="mb-4">
          <h2 className="text-xs font-medium text-gray-700 uppercase mb-2">
            WHEN TO HELP
          </h2>
          <div className="relative">
            <select className="w-full p-3 bg-white border border-gray-200 rounded-lg text-gray-700 appearance-none pr-8">
              <option>Today, 9:00 AM - 12:00 PM</option>
              <option>Today, 12:00 PM - 3:00 PM</option>
              <option>Today, 3:00 PM - 6:00 PM</option>
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
              {opportunity.location} Center
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col gap-2">
          <Button
            className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg"
            onClick={() =>
              console.log("Volunteer signup", {
                opportunityId: id,
                tasks: tasks.filter((t) => t.checked),
              })
            }
          >
            Join Now
          </Button>
          <Link href="/" className="w-full text-center">
            <button className="w-full text-gray-700 py-2 px-4">Cancel</button>
          </Link>
        </div>
      </div>
    </div>
  );
}
