import React from "react";

const ShimmerLoader = ({ width = "100%", height = "20px", className = "", error }) => {
  return (
    <>
    <div
      className={`flex relative overflow-hidden bg-gray-300 rounded ${className}`}
      style={{ width, height }}
    ><span className="mx-auto my-auto text-gray-400 font-semibold">{!error ? "Loading..." : "Error"}</span>
      <div className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent from-30% via-white via-50% to-transparent to-80%"
      style={{ 
        backgroundSize: "200% 100%",
        animation: "shimmer 2.5s infinite ease-in-out"
       }} />
    </div>
        <style>
            {!error && `
            @keyframes shimmer {
                0% {
                background-position: -200% 0;
                }
                100% {
                background-position: 200% 0;
                }
            }
            `}
        </style>
    </>
  );
};

export default ShimmerLoader;