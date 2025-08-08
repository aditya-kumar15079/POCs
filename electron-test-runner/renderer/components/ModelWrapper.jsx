import React, { useEffect } from "react";

const ModalWrapper = ({ isOpen, onClose, children, width = "max-w-3xl" }) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") onClose?.();
    };

    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    }

    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70" onClick={onClose}>
      <div className={`bg-white rounded-lg shadow-lg w-full ${width} relative p-4`} onClick={(e) => e.stopPropagation()}>
        <button
          type="button"
          className="absolute top-2 right-3 text-gray-600 text-2xl font-bold hover:text-gray-800"
          onClick={onClose}
          aria-label="Close"
        >
          &times;
        </button>
        {children}
      </div>
    </div>
  );
};

export default ModalWrapper;
