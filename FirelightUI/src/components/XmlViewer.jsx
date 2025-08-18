import { CheckLine, Circle, CircleCheck, Copy, Verified } from "lucide-react";
import React, { use, useEffect, useRef } from "react";

const XmlViewer = ({ xml }) => {
  const [copied, setCopied] = React.useState(0);
  const xmlRef = useRef(null);
  const [verifyText, setVerifyText] = React.useState("Verify");

  const handleCopy = () => {
    if (xmlRef.current) {
      setCopied(2);
      navigator.clipboard.writeText(xml);
    }
  };

  const handleVerify = () => {
    setVerifyText("Verified");
  }

  useEffect(() => {
    if (copied === 2) {
      setTimeout(() => {
        setCopied(3);
      }, 500);
    }
    if (copied === 3) {
      setTimeout(() => {
        setCopied(1);
      }, 4000);
    }
  }, [copied]);

  const getCopySymbol = () => {
    if (copied === 2) {
      return <Circle fill="gray" size={12} />;
    } else if (copied === 3) {
      return <CircleCheck fill="green" size={12} />;
    }
    return <Copy size={12} />;
  };
  return (
    <div className={`rounded-lg p-4 ${verifyText === "Verified" ? "bg-green-100/60" : "bg-gray-100"} relative shadow-sm overflow-x-auto`} style={{ scrollbarWidth: "none"}}>
      {xml ? (
        <>
          <pre
            ref={xmlRef}
            className="text-sm text-gray-800 whitespace-pre overflow-x-auto"
            dangerouslySetInnerHTML={{ __html: escapeXml(xml) }}
          />

          <div className="absolute top-2 right-2 flex gap-1">
            <div
            onClick={handleVerify}
            className={`flex gap-1 items-center ${verifyText === "Verified" ? "bg-gray-600" : "bg-gray-300"} text-sm text-white px-2 rounded hover:bg-gray-600 transition`}
          >
            {verifyText} {verifyText === "Verified" && <CheckLine size={16} />}
          </div>

          <button
            onClick={handleCopy}
            className={`${copied > 0 ? "bg-gray-600" : "bg-gray-300"} text-white p-2 rounded hover:bg-gray-600 transition`}
          >
            {getCopySymbol()}
          </button>
          </div>
        </>
      ) : (
        <>
        <pre>Something went wrong</pre>
        </>
        
      )}
    </div>
  );
};

// Escape XML for safe rendering
function escapeXml(xml) {
  return xml?.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export default XmlViewer;
