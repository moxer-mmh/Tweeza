"use client";
import React from "react";
import { useState } from "react";
import EmergencyCard from "@/components/EmergencyCard";
import AssistanceCard from "@/components/AssistanceCard";
import EventCard from "@/components/EventCard";

const Page = () => {
  const [activeTab, setActiveTab] = useState("Emergency");

  const mockData = {
    Emergency: [
      {
        id: 1,
        title: "Food Bank",
        description: "Local food distribution center needs supplies",
        location: "Downtown",
        urgency: "High",
        quantity: { current: 30, needed: 100 },
        deadline: "2024-02-01",
      },
      {
        id: 2,
        title: "Community Garden",
        description: "Seeds and tools needed for spring planting",
        location: "Westside",
        urgency: "Medium",
        quantity: { current: 45, needed: 80 },
        deadline: "2024-02-15",
      },
      {
        id: 3,
        title: "Tool Library",
        description: "Construction tools needed for rebuilding",
        location: "Eastside",
        urgency: "High",
        quantity: { current: 15, needed: 50 },
        deadline: "2024-01-30",
      },
    ],
    assistance: [
      {
        id: 1,
        title: "Legal Aid",
        description: "Free legal consultation",
        location: "City Center",
        coordinates: { lat: 40.7528, lng: -74.026 },
      },
      {
        id: 2,
        title: "Housing Assistance",
        description: "Help finding affordable housing",
        location: "Northside",
        coordinates: { lat: 40.7628, lng: -74.036 },
      },
      {
        id: 3,
        title: "Financial Counseling",
        description: "Budget and debt advice",
        location: "Southside",
        coordinates: { lat: 40.7028, lng: -73.986 },
      },
    ],
    events: [
      {
        id: 1,
        title: "Community Cleanup",
        description: "Volunteer event to clean local park",
        location: "Central Park",
        coordinates: { lat: 40.7828, lng: -73.966 },
      },
      {
        id: 2,
        title: "Farmers Market",
        description: "Weekly local produce market",
        location: "Market Square",
        coordinates: { lat: 40.7428, lng: -73.976 },
      },
      {
        id: 3,
        title: "Workshop Series",
        description: "DIY repair workshops",
        location: "Community Center",
        coordinates: { lat: 40.7328, lng: -74.046 },
      },
    ],
  };

  // Get data based on active tab
  const activeData = mockData[activeTab] || [];

  return (
    <div className="container mx-auto  pb-8">
      <div className="relative">
        <div className="absolute left-1/2 -translate-x-1/2 top-4 z-10 flex items-center gap-2 w-3/4 md:w-1/4 max-w-4xl ">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Search locations..."
              className="w-full pl-10 pr-4 py-1 text-black rounded-lg focus:outline-none focus:border-red-700 bg-white "
            />
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
          </div>
        </div>
        <div className="absolute right-4 top-2 z-10">
          <button className="p-2 h-10 w-10 bg-white border-2 shadow-md border-[#E8E8E8] rounded-full hover:shadow-lg transition-shadow">
            <svg
              className=" text-gray-600"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </button>
        </div>
        <div className="bg-gray-100 rounded-lg p-4  h-[400px] relative">
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-gray-500"></p>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div>
        <div className="mb-6   px-4">
          <div className="flex  justify-center items-center border-b border-gray-300">
            <button
              onClick={() => setActiveTab("Emergency")}
              className={`py-2 px-4 font-medium  ${
                activeTab === "Emergency"
                  ? "text-[#973535] border-b-2 border-[#973535]"
                  : "text-gray-500"
              }`}
            >
              Emergency
            </button>
            <button
              onClick={() => setActiveTab("assistance")}
              className={`py-2 px-4 font-medium ${
                activeTab === "assistance"
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-500"
              }`}
            >
              Assistance
            </button>
            <button
              onClick={() => setActiveTab("events")}
              className={`py-2 px-4 font-medium ${
                activeTab === "events"
                  ? "text-emerald-600 border-b-2 border-emerald-600"
                  : "text-gray-500"
              }`}
            >
              Events
            </button>
          </div>
        </div>

        {/* Results List */}
        <div className="grid px-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {activeTab === "Emergency"
            ? activeData.map((item) => (
                <EmergencyCard
                  key={item.id}
                  id={item.id}
                  title={item.title}
                  description={item.description}
                  location={item.location}
                  urgency={item.urgency}
                  quantity={item.quantity}
                  deadline={item.deadline}
                />
              ))
            : activeTab === "assistance"
            ? activeData.map((item) => (
                <AssistanceCard
                  key={item.id}
                  title={item.title}
                  description={item.description}
                  location={item.location}
                  coordinates={item.coordinates}
                />
              ))
            : activeData.map((item) => (
                <EventCard
                  key={item.id}
                  title={item.title}
                  description={item.description}
                  location={item.location}
                  date={new Date().toISOString()}
                  attendees={{ current: 15 }}
                />
              ))}
        </div>

        {/* Empty State */}
        {activeData.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No {activeTab} found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Page;
