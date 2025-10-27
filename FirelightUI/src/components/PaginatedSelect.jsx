import React, { useState, useRef, useEffect } from "react";

const PaginatedSelect = ({
  label,
  options = [],
  value,
  onChange,
  name,
  initialCount = 5,
  increment = 3,
  width = 3,
  view = "column",
  enabled = true
}) => {
  const [open, setOpen] = useState(false);
  const [visibleCount, setVisibleCount] = useState(initialCount);
  const dropdownRef = useRef(null);

  useEffect(() => {
    setVisibleCount(initialCount);
  }, [options, initialCount]);

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (selectedValue) => {
    if (selectedValue === "__SEE_MORE__") {
      setVisibleCount((prev) => Math.min(prev + increment, options.length));
      return;
    }
    onChange({ target: { name, value: selectedValue } });
    setOpen(false);
  };

  const selectedOption = options.find((opt) => opt.value === value);

  const styleWidth = parseInt(width) % 13;

  return (
    <div className={`relative my-2 ${view === "row" ? "flex gap-2" : ""}`} ref={dropdownRef} style={{ width: styleWidth * 100 - 20 }}>
      {label && (
        <label htmlFor={name} className="w-2/5 text-sm font-medium text-black mb-1">
          {label}
        </label>
      )}
      <button
        type="button"
        enabled={enabled}
        onClick={() => setOpen((prev) => !prev)}
        className={`${view === "column" ? "w-full" : "w-3/5 ml-4"} h-8 border border-gray-300 rounded px-3 py-1 bg-white text-sm text-left text-black focus:outline-none focus:ring-1 focus:ring-blue-500`}
      >
        {selectedOption ? selectedOption.label : "-select-"}
      </button>

      {open && (
        <div className={`absolute z-10 top-7 right-[-5px] mt-1 ${view === "column" ? "w-full" : "w-3/5"} bg-white border border-gray-300 rounded shadow-lg max-h-60 overflow-auto`}>
          {options.slice(0, visibleCount).map((opt) => (
            <div
              key={opt.value}
              onClick={() => handleSelect(opt.value)}
              className={`px-3 py-2 cursor-pointer hover:bg-blue-100 text-sm ${
                value === opt.value ? "bg-blue-50 font-semibold" : ""
              }`}
            >
              {opt.label}
            </div>
          ))}
          {options.length > visibleCount && (
            <div
              onClick={() => handleSelect("__SEE_MORE__")}
              className="px-3 py-2 cursor-pointer text-blue-600 hover:bg-gray-100 italic text-sm font-medium"
            >
              + See more...
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PaginatedSelect;
