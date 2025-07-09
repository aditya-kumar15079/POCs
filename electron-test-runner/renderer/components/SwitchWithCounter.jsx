import React, { useEffect } from "react";

export const SwitchWithCounter = ({ title, description, count, setCount, isEnabled, toggleSwitch, disabled = false }) => {
  useEffect(() => {
    if (!isEnabled) {
      setCount(0);
    }
  }, [isEnabled]);
  return (
    <div className={`border p-4 bg-white rounded shadow-sm ${disabled ? "opacity-50" : ""}`}>
      <div className="flex justify-between items-center mb-2 border-b pb-2">
        <h3 className="font-semibold text-gray-700">{title}</h3>
        <label className="inline-flex items-center cursor-pointer">
          <input type="checkbox" checked={isEnabled} onChange={toggleSwitch} disabled={disabled} className="sr-only" />
          <div className={`w-10 h-6 rounded-full transition ${isEnabled ? "bg-blue-600" : "bg-gray-300"}`}></div>
        </label>
      </div>
      <div className="flex justify-center text-gray-400 m-4">{description}</div>

      <div className="flex items-center space-x-2">
        <button onClick={() => setCount(Math.max(count - 1, 1))} className="px-2 py-1 bg-gray-200 rounded" disabled={!isEnabled}>
          -
        </button>
        <span>{count.toString().padStart(2, "0")}</span>
        <button onClick={() => setCount(count + 1)} className="px-2 py-1 bg-gray-200 rounded" disabled={!isEnabled}>
          +
        </button>
      </div>
    </div>
  );
};
