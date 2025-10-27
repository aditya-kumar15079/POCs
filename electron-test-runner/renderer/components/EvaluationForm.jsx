import React, { useState, useEffect } from "react";
import ToggleSwitch from "./ToggleSwitch";

const EvaluationForm = ({ id }) => {
  const [fileConfig, setFileConfig] = useState(null);
  const updateFileContent = async (content) => {
    await window.api.writeYAML(content, getConfigFile(id));
  };

  const getConfigFile = (id) => {
    if (id === 102) {
      return "Test-Foundry/GENAI_LLMJudge_ResponseQuality_Framework/config.yaml";
    } else if (id === 103) {
      return "Test-Foundry/GENAI_Compass/config.yaml";
    }
    return null;
  };

  const readConfig = async () => {
    const config = await window.api.readYAML(getConfigFile(id));
    if (config) {
      setFileConfig(config);
    }
  };

  useEffect(() => {
    readConfig();
  }, [id]);

  useEffect(() => {
    updateFileContent(fileConfig);
  }, [fileConfig]);

  const executeTest = () => {
    let executeFilePath = "";
    if (id === 102) {
      executeFilePath = "Test-Foundry/GENAI_LLMJudge_ResponseQuality_Framework/Execute.bat";
    } else if (id === 103) {
      executeFilePath = "Test-Foundry/GENAI_Compass/Execute.bat";
    }
    window.api.executeTest(executeFilePath);
  };

  const toggleMetric = (metric) => {
    setFileConfig((prev) => ({
      ...prev,
      evaluation: {
        ...prev?.evaluation,
        metrics: {
          ...prev?.evaluation?.metrics,
          [metric]: !prev?.evaluation?.metrics?.[metric],
        },
      },
    }));
  };

  return (
    <>
      <div className="flex justify-between">
        <span className="font-semibold text-gray-500 ml-2">Evaluation Meterics</span>
        <button className="text-sm text-blue-600 mr-2">View Previous Evaluation</button>
      </div>
      <div className="mx-auto bg-white border border-gray-300 rounded-lg shadow p-6">
        <div className="space-y-4">
          {Object.entries(fileConfig?.evaluation?.metrics || {}).map(([label, value]) => (
            <div key={label} className="flex items-center justify-between">
              <label className="text-gray-700 flex items-center gap-1">{label}</label>
              <label className="inline-flex items-center cursor-pointer">
                <input type="checkbox" checked={value} onChange={() => toggleMetric(label)} className="sr-only" />
                {/* {value ? <ToggleLeft className="w-6 h-6 text-gray-500" /> : <ToggleRight className="w-6 h-6 text-green-500" />} */}
                <ToggleSwitch isOn={value} />
              </label>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-6 bg-white p-4 shadow rounded">
        <h3 className="text-md font-semibold mb-2 text-gray-500 border-b pb-2">Upload Document</h3>
        <input
          type="file"
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
      </div>
      <div className="flex justify-end">
        <button className="btn-primary" onClick={executeTest}>
          Execute Evaluation
        </button>
      </div>
    </>
  );
};

export default EvaluationForm;
