import React, { useEffect, useRef, useState } from "react";
import Loader from "./Loader";

const Spinner = ({ message = "Loading" }) => {
  const [dots, setDots] = useState(".");
  const interval = useRef(null);

  useEffect(() => {
    interval.current = setInterval(() => {
      setDots((prevDots) => (prevDots.length < 3 ? prevDots + "." : "."));
    }, 500);

    return () => {
      clearInterval(interval.current);
    };
  }, []);

  return (
    <div className="fixed inset-0 w-screen h-screen bg-black/40 flex justify-center items-center z-[1000]">
      <div className="bg-white p-8 rounded-[10px] text-center shadow-[0_2px_15px_rgba(0,0,0,0.2)]">
        <div className="mx-auto mb-4 w-10 h-10 border-[5px] border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
        <p className="text-[1.2rem] font-medium min-w-30">
          {message} {dots}
        </p>
      </div>
    </div>
  );
};

const spinnerStyle = document.createElement("style");
spinnerStyle.innerHTML = `
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}`;
document.head.appendChild(spinnerStyle);

export default Spinner;
