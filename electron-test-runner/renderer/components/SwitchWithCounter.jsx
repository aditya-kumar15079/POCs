import { ToggleLeft, ToggleRight } from "lucide-react";
import React, { useEffect } from "react";
import ToggleSwitch from "./ToggleSwitch";

export const SwitchWithCounter = ({ title, description, count, setCount, isEnabled, toggleSwitch, disabled = false }) => {
  useEffect(() => {
    if (!isEnabled) {
      setCount(0);
    }
  }, [isEnabled]);
  return (
    <div className={`p-4 bg-white rounded shadow-sm ${disabled ? "opacity-50" : ""}`}>
      <div className="flex justify-between items-center mb-2 border-b border-gray-300 pb-2">
        <h3 className="font-semibold text-gray-700">{title}</h3>
        <label className="inline-flex items-center cursor-pointer">
          <input type="checkbox" checked={isEnabled} onChange={toggleSwitch} disabled={disabled} className="sr-only" />
          <ToggleSwitch isOn={isEnabled} />
        </label>
      </div>
      <div className="flex justify-center text-gray-500 m-4">{description}</div>

      <div className="flex items-center space-x-2">
        <button onClick={() => setCount(Math.max(count - 1, 0))} className="px-2 py-1 bg-gray-200 rounded" disabled={!isEnabled}>
          -
        </button>
        <input
          type="tel"
          value={count || 0}
          onChange={(e) => setCount((prev) => parseInt(e.target.value || 0))}
          className="w-12 text-center"
          disabled={!isEnabled}
        />
        <button onClick={() => setCount(count + 1)} className="px-2 py-1 bg-gray-200 rounded" disabled={!isEnabled}>
          +
        </button>
      </div>
    </div>
  );
};
