"use client";

import { useState } from "react";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState("events");

  // Mock user data
  const userData = {
    name: "Alex Johnson",
    email: "alex.johnson@example.com",
    phone: "(555) 123-4567",
    events: [
      {
        id: 1,
        title: "Community Fundraiser",
        location: "City Park (2.5 miles away)",
        date: "March 25, 2024",
        time: "4:00 PM - 8:00 PM",
        status: "Attending",
      },
      {
        id: 2,
        title: "Community Fundraiser",
        location: "City Park (2.5 miles away)",
        date: "March 25, 2024",
        time: "4:00 PM - 8:00 PM",
        status: "Attending",
      },
      {
        id: 3,
        title: "Community Fundraiser",
        location: "City Park (2.5 miles away)",
        date: "March 25, 2024",
        time: "4:00 PM - 8:00 PM",
        status: "Attending",
      },
    ],
    donations: [
      {
        id: 1,
        organization: "Community Center",
        items: [
          { name: "Bottled Water", quantity: 24 },
          { name: "Blankets", quantity: 12 },
          { name: "Canned Food", quantity: 20 },
        ],
        status: "Done",
        delivery: { date: "Today", time: "10:00 AM - 12:00 PM" },
      },
      {
        id: 2,
        organization: "Community Center",
        items: [
          { name: "Bottled Water", quantity: 24 },
          { name: "Blankets", quantity: 12 },
          { name: "Canned Food", quantity: 20 },
        ],
        status: "Incoming",
        delivery: { date: "Today", time: "10:00 AM - 12:00 PM" },
      },
    ],
  };

  return (
    <div className="container max-w-4xl mx-auto px-4 py-8">
      {/* Profile Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link
          href="/"
          className=" hover:text-gray-800 flex justify-center items-center w-[46px] shadow-md bg-[#E8F5E9] border-[#E8E8E8] border-2 rounded-2xl p-1 "
        >
          <ChevronLeft className="h-6 w-6" />
        </Link>
        <h1 className="text-2xl font-semibold">My Profile</h1>
      </div>

      {/* User Info Card */}
      <div className="bg-white rounded-2xl border-2 border-[#E8E8E8] shadow-md p-3 mb-8">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center text-xl font-semibold">
            {userData.name
              .split(" ")
              .map((n) => n[0])
              .join("")}
          </div>
          <div className="text-[#71717A]">
            <h2 className="text-xl text-black font-semibold">
              {userData.name}
            </h2>
            <p className="">{userData.email}</p>
            <p className="">{userData.phone}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab("events")}
          className={`pb-4 px-4 text-sm font-medium ${
            activeTab === "events"
              ? "text-emerald-600 border-b-2 border-emerald-600"
              : "text-gray-500"
          }`}
        >
          Events You're Attending
        </button>
        <button
          onClick={() => setActiveTab("donations")}
          className={`pb-4 px-4 text-sm font-medium ${
            activeTab === "donations"
              ? "text-emerald-600 border-b-2 border-emerald-600"
              : "text-gray-500"
          }`}
        >
          Your Pending Donations
        </button>
      </div>

      {/* Content */}
      <div className="space-y-4">
        {activeTab === "events"
          ? userData.events.map((event) => (
              <div
                key={event.id}
                className="bg-white rounded-lg border-2 border-[#E8E8E8] shadow-sm p-4  s"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold ">{event.title}</h3>
                  <span className="px-2 py-1 bg-emerald-50 text-emerald-600 rounded-full text-xs font-medium">
                    {event.status}
                  </span>
                </div>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                    </svg>
                    {event.location}
                  </div>
                  <div className="flex items-center gap-2">
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    {event.date}
                  </div>
                  <div className="flex items-center gap-2">
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    {event.time}
                  </div>
                </div>
                <button className="mt-4 text-sm text-emerald-600 font-medium">
                  View Details
                </button>
              </div>
            ))
          : userData.donations.map((donation) => (
              <div
                key={donation.id}
                className="bg-white rounded-lg shadow-sm p-4 border border-gray-100"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-medium">{donation.organization}</h3>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      donation.status === "Done"
                        ? "bg-emerald-50 text-emerald-600"
                        : "bg-blue-50 text-blue-600"
                    }`}
                  >
                    {donation.status}
                  </span>
                </div>
                <div className="space-y-2">
                  <h4 className="text-xs font-medium text-gray-500 uppercase">
                    ITEMS TO DONATE:
                  </h4>
                  <div className="space-y-1">
                    {donation.items.map((item, index) => (
                      <div key={index} className="flex justify-between text-sm">
                        <span>{item.name}</span>
                        <span>x {item.quantity}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    Delivery: {donation.delivery.date}, {donation.delivery.time}
                  </div>
                </div>
                <button className="mt-4 text-sm text-emerald-600 font-medium">
                  {donation.status === "Done" ? "View Details" : "Track Status"}
                </button>
              </div>
            ))}
      </div>
    </div>
  );
}
