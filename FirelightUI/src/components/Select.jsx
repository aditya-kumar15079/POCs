import React from "react";

const Select = ({ label, options = [], value, onChange, name, width = 3 }) => {

    const styleWidth = parseInt(width) % 13

  return (
    <div className={`flex flex-col gap-1`} style={{ width: styleWidth * 100 - 20 }} >
      {label && (
        <label htmlFor={name} className="text-sm font-semibold text-black">
          {label}
        </label>
      )}
      <select
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        className="border border-gray-300 rounded px-3 py-2 bg-white text-sm text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="" disabled>
          -- Select an option --
        </option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Select;
