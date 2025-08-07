import React from "react";
import { Download } from "lucide-react"; // or use any other icon library

const PreviousEvaluation = ({ files }) => {
  return (
    <div className="w-full mx-auto bg-white rounded-md p-2">
      <h2 className="text-lg font-semibold">View Previous Evaluation</h2>
      <div className="overflow-auto max-h-150">
        <table className="w-full text-left border-separate border-spacing-y-2">
          <thead>
            <tr className="text-sm font-medium text-gray-600">
              <th>File Name</th>
              <th>Date & Time</th>
              <th>Download</th>
            </tr>
          </thead>
          <tbody>
            {files.map((file, index) => (
              <tr key={index} className="text-sm text-gray-700 bg-gray-50 rounded">
                <td className="py-2">{file.name}</td>
                <td className="py-2">{file.datetime}</td>
                <td className="py-2">
                  <a href={file.downloadUrl} className="text-blue-600 hover:text-blue-800">
                    <Download size={18} />
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PreviousEvaluation;