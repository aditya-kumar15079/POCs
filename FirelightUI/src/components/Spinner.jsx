import React, { useEffect, useRef, useState } from "react";

const Spinner = ({ message = "Loading", dot = ".", spinner = true }) => {
  const [dots, setDots] = useState(dot);
  const interval = useRef(null);

  useEffect(() => {
    interval.current = setInterval(() => {
      setDots((prevDots) => (prevDots.length < 3 ? prevDots + dot : dot));
    }, 500);

    return () => {
      clearInterval(interval.current);
    };
  }, []);

  return !spinner ? (
    <p>
      {message} {dots}
    </p>
  ) : (
    <div className="flex justify-center items-center">
      <div className="p-8 rounded-[10px] text-center">
        <div className="mx-auto mb-4 w-10 h-10 border-[5px] border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
        <p className="text-[1.2rem] min-w-30 text-gray-500">
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
