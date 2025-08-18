import React from "react";
import {
  ChevronLeft,
  ChevronRight,
  Pencil,
  Copy,
  Trash,
  Info,
} from "lucide-react";

const Input = (props) => {
  const {
    title,
    width = 3,
    type,
    placeholder,
    value,
    onChange,
    error,
    id,
    selected,
    onClick,
    showPopUp,
    onKeyUp,
  } = props;

  const styleWidth = parseInt(width) % 13;

  return (
    <div
      className={`flex flex-col gap-1 mt-4 p-1 relative
        ${selected ? "border-2 border-hexorange -translate-y-1" : ""}`}
      onClick={() => onClick && onClick(id)}
    >
      <label className="font-semibold">{title}</label>
      <div className="flex">
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className={`p-2 outline-none ${
            error ? "border-2 border-red-500" : "border"
          }`}
          onKeyUp={(event) => onKeyUp && onKeyUp(event)}
          style={{ width: styleWidth * 100 - 20 }}
        />
        {error && (
          <div className="relative flex items-center justify-center group ml-[-32px]">
            <Info className="text-red-500 text-sm self-center" />
            <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded px-2 py-1 whitespace-nowrap z-10">
              {error}
            </div>
          </div>
        )}
      </div>

      {selected && (
        <div
          className="flex gap-1 items-center p-4 bg-hexorange text-white text-2xl font-bold text-center"
          style={{ position: "absolute", top: "-75%", left: "-2px" }}
        >
          <ChevronLeft className="w-5 h-5 text-white" />
          <span className="font-normal text-sm">Width: {width} of 12</span>
          <ChevronRight className="w-5 h-5 text-white" />
          <Pencil
            className="w-6 h-6 ml-12 mr-2 text-white hover:cursor-pointer"
            onClick={(event) => showPopUp(event)}
          />
          <Copy className="w-5 h-5 mx-2 text-white" />
          <Trash className="w-5 h-5 mx-2 text-white" />
        </div>
      )}
    </div>
  );
};

export default Input;
