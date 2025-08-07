import { useState } from "react";
import { ToggleLeft, ToggleRight } from "lucide-react";

function ToggleSwitch({ isOn, size = 42, color = "white" }) {
  // const [isOn, setIsOn] = useState(false);

  return (
    <div
      style={{
        backgroundColor: isOn ? "#008f0a" : "#b5b5b5",
        borderRadius: "40%",
        transition: "background-color 0.3s ease",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        border: "none",
        cursor: "pointer",
        width: size - size / 5,
        height: size - size / 2.5,
        position: "relative",
      }}
      aria-label="Toggle switch"
    >
      {isOn ? (
        <ToggleRight
          size={size}
          color={color}
          strokeWidth={2}
          absoluteStrokeWidth={true}
          style={{
            transition: "transform 0.3s ease",
            position: "absolute",
          }}
        />
      ) : (
        <ToggleLeft
          size={size}
          color={color}
          strokeWidth={2}
          absoluteStrokeWidth={true}
          style={{
            transition: "transform 0.3s ease",
            position: "absolute",
          }}
        />
      )}
    </div>
  );
}

export default ToggleSwitch;
