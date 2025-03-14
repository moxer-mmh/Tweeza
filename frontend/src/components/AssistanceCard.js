import React from "react";
import Link from "next/link";

const AssistanceCard = ({
  id,
  title,
  description,
  location,
  coordinates,
  deadline,
  quantity = { current: 0, needed: 100 },
}) => {
  return (
    <div className="border h-[290px] border-[#E8E8E8] rounded-[16px] overflow-hidden shadow-md hover:shadow-lg transition-shadow bg-white">
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-semibold">{title}</h3>
          <span className="px-2 py-1 rounded-[16px] border-2 border-[#E8E8E8] p-2 text-sm shadow-md bg-[#E8F5E9] text-blue-600">
            Available
          </span>
        </div>
        <p className="text-gray-600 mb-4">{description}</p>
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm text-gray-500 mb-1">
            <span>Support Status</span>
            <span>
              {quantity.current}/{quantity.needed}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 rounded-full h-2"
              style={{
                width: `${(quantity.current / quantity.needed) * 100}%`,
              }}
            />
          </div>
        </div>
        <div className="flex flex-col text-gray-500 mb-4">
          <div className="flex items-center text-gray-500 mb-3">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-1"
              viewBox="0 0 20 20"
              fill="black"
            >
              <path
                fillRule="evenodd"
                d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-sm">
              Deadline: {new Date(deadline).toLocaleDateString()}
            </span>
          </div>
          <div className="flex">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-1"
              viewBox="0 0 20 20"
              fill="black"
            >
              <path
                fillRule="evenodd"
                d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-sm">{location}</span>
          </div>
        </div>{" "}
        <div className="flex space-x-2">
          <button className="flex-1 rounded-[16px] border-2 border-[#E8E8E8] bg-blue-600 text-white py-2 px-4 hover:bg-blue-700 transition-colors">
            Contribute Now
          </button>
          <Link href={`/volunteer/${id}`} className="flex-1">
            <button className="w-full border-2 border-[#E8E8E8] rounded-[16px] text-blue-600 py-2 px-4 hover:bg-gray-50 transition-colors">
              View Details
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AssistanceCard;
