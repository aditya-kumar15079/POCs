import React from "react";

export const DropdownSelect = ({ label, options, onSelected }) => {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <select
        className="w-full border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        onChange={(event) => onSelected(event.target.value)}
      >
        {options.map((option, index) => (
          <option key={index} value={index}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
};
