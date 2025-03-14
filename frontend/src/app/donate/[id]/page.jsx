"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

export default function DonatePage() {
  const { id } = useParams();
  const [emergency, setEmergency] = useState(null);
  const [items, setItems] = useState([]);

  useEffect(() => {
    // In a real application, you would fetch the emergency details from an API
    // For now, we'll simulate it with mock data
    const mockEmergency = {
      id: parseInt(id),
      title: "Food Bank",
      location: "City Park",
      deadline: "2024-04-01",
      items: [
        { id: 1, name: "Bottled Water", quantity: 0, needed: 50, urgent: true },
        { id: 2, name: "Canned Food", quantity: 0, needed: 100, urgent: true },
        { id: 3, name: "Blankets", quantity: 0, needed: 30, urgent: false },
      ],
    };

    setEmergency(mockEmergency);
    setItems(mockEmergency.items);
  }, [id]);

  const handleQuantityChange = (itemId, change) => {
    setItems(
      items.map((item) => {
        if (item.id === itemId) {
          return { ...item, quantity: Math.max(0, item.quantity + change) };
        }
        return item;
      })
    );
  };

  if (!emergency) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container max-w-md mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link href="/" className="text-gray-600 hover:text-gray-800">
          <ChevronLeft className="h-6 w-6" />
        </Link>
        <h1 className="text-[18px] font-semibold">Donate Resources</h1>
      </div>
      <div className="border border-[#E8E8E8] p-4 rounded-[16px] shadow-md bg-white">
        {/* Location and Time */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <span className="font-semibold text-[16px]">
                {emergency.location}
              </span>
            </div>
            <div className="flex items-center">
              <span className="text-sm text-gray-500 mr-1">•</span>
              <span className="text-sm text-gray-500">
                Needed by: {new Date(emergency.deadline).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        {/* Items Selection */}
        <div className="space-y-3 mb-4">
          <h2 className="text-xs font-medium text-gray-700 uppercase">
            SELECT ITEMS & QUANTITIES
          </h2>
          {items.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm">{item.name}</span>
                  {item.urgent && (
                    <span className="px-2 py-0.5 text-xs font-medium text-red-700 bg-red-50 rounded-full">
                      Urgent
                    </span>
                  )}
                </div>
                <div className="text-xs text-gray-500">
                  Needed: {item.needed} / 200
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleQuantityChange(item.id, -1)}
                  className="w-7 h-7 flex items-center justify-center rounded-full border border-gray-300 text-gray-600 hover:bg-gray-50"
                  disabled={item.quantity === 0}
                >
                  -
                </button>
                <span className="w-6 text-center">{item.quantity}</span>
                <button
                  onClick={() => handleQuantityChange(item.id, 1)}
                  className="w-7 h-7 flex items-center justify-center rounded-full border border-gray-300 text-gray-600 hover:bg-gray-50"
                >
                  +
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Delivery Time */}
        <div className="mb-4">
          <h2 className="text-xs font-medium text-gray-700 uppercase mb-2">
            WHEN CAN YOU DELIVER?
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

        {/* Drop-off Location */}
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
              Drop-off at {emergency.location} Center
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col gap-2">
          <Button
            className="w-full bg-red-700 hover:bg-red-800 text-white py-2 px-4 rounded-lg"
            onClick={() =>
              console.log("Confirm donation", { emergencyId: id, items })
            }
          >
            Confirm Donation
          </Button>
          <Link href="/" className="w-full text-center">
            <button className="w-full text-gray-700 py-2 px-4">Cancel</button>
          </Link>
        </div>
      </div>
    </div>
  );
}
