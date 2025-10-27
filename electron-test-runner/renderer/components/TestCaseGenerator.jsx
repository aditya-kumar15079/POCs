import React, { useEffect, useState } from "react";
import { SwitchWithCounter } from "./SwitchWithCounter";
import { debounce } from "../utils/Helpers";
import ModalWrapper from "./ModelWrapper";
import PreviousEvaluation from "./PreviousEvaluation";

const TestCaseGenerator = () => {
  const [qaCount, setQaCount] = useState(0);
  const [qaEnabled, setQaEnabled] = useState(true);
  const [advCount, setAdvCount] = useState(0);
  const [advEnabled, setAdvEnabled] = useState(true);
  const [biasCount, setBiasCount] = useState(0);
  const [biasEnabled, setBiasEnabled] = useState(false);
  const [hallCount, setHallCount] = useState(0);
  const [hallEnabled, setHallEnabled] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [fileConfig, setFileConfig] = useState(null);

  const [files, setFiles] = useState([]);
  const [outputFiles, setOutputFiles] = useState([]);

  let saveTimeout = null;
  const filePath = "Test-Foundry/TestFoundry_Framework/config.yaml";
  const updateFileContent = async (content) => {
    await window.api.writeYAML(content, filePath);
  };
  const debouncedUpdateFileContent = React.useMemo(() => debounce(updateFileContent, 500), []);

  const fetchOutputFiles = async () => {
    const files = await window.api.listFiles("Test-Foundry/TestFoundry_Framework/output");
    console.log("Formatted Files:", files);
    setOutputFiles(files);
  };

  const onMount = () => {
    readConfig();
    fetchOutputFiles();
  };

  useEffect(() => {
    onMount();
  }, []);

  useEffect(() => {
    debouncedUpdateFileContent(fileConfig);
  }, [fileConfig]);

  useEffect(() => {
    const config = {
      ...fileConfig,
      qa_generation: {
        ...fileConfig?.qa_generation,
        enabled: qaEnabled,
        questions_per_document: qaCount,
      },
      test_case_generation: {
        ...fileConfig?.test_case_generation,
        types: {
          ...fileConfig?.test_case_generation?.types,
          adversarial: {
            ...fileConfig?.test_case_generation?.types?.adversarial,
            enabled: advEnabled,
            questions_per_type: advCount,
          },
          bias: {
            ...fileConfig?.test_case_generation?.types?.bias,
            enabled: biasEnabled,
            questions_per_type: biasCount,
          },
          hallucination: {
            ...fileConfig?.test_case_generation?.types?.hallucination,
            enabled: hallEnabled,
            questions_per_type: hallCount,
          },
        },
      },
    };
    setFileConfig(config);
    console.log("setFileConfigs");
  }, [qaCount, qaEnabled, advCount, advEnabled, biasCount, biasEnabled, hallCount, hallEnabled]);

  const readConfig = async () => {
    const config = await window.api.readYAML(filePath);
    if (!config) return;
    setFileConfig(config);
    setQaEnabled(config?.qa_generation?.enabled || false);
    setQaCount(config?.qa_generation?.questions_per_document || 0);
    setAdvEnabled(config?.test_case_generation?.types?.adversarial?.enabled || false);
    setAdvCount(config?.test_case_generation?.types?.adversarial?.questions_per_type || 0);
    setBiasEnabled(config?.test_case_generation?.types?.bias?.enabled || false);
    setBiasCount(config?.test_case_generation?.types?.bias?.questions_per_type || 0);
    setHallEnabled(config?.test_case_generation?.types?.hallucination?.enabled || false);
    setHallCount(config?.test_case_generation?.types?.hallucination?.questions_per_type || 0);
  };

  const handleFilesChange = (e) => {
    const newFiles = Array.from(e.target.files);
    setFiles((prevFiles) => {
      const existingKeys = new Set(prevFiles.map((f) => f.name + f.size));
      const combined = [...prevFiles];
      newFiles.forEach((f) => {
        const key = f.name + f.size;
        if (!existingKeys.has(key)) {
          combined.push(f);
          existingKeys.add(key);
        }
      });
      return combined;
    });
    e.target.value = null;
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const executeTest = () => {
    window.api.executeTest("Test-Foundry/TestFoundry_Framework/Execute.bat");
  };

  const handleViewPreviousEvaluation = () => {
    setIsModalOpen(true);
    fetchOutputFiles();
  };

  return (
    <>
      <div className="flex justify-between">
        <span className="font-semibold text-gray-500 ml-2">QA Generation Settings</span>
        <button className="text-sm text-primary hover:text-primary-hover mr-2" onClick={handleViewPreviousEvaluation}>
          View Previous Evaluation
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SwitchWithCounter
          title="Generate QnA Pairs"
          description="Questions Per Document"
          count={qaCount}
          setCount={setQaCount}
          isEnabled={qaEnabled}
          toggleSwitch={() => setQaEnabled(!qaEnabled)}
        />
        <SwitchWithCounter
          title="Adversarial Test Cases"
          description="Number of Questions"
          count={advCount}
          setCount={setAdvCount}
          isEnabled={advEnabled}
          toggleSwitch={() => setAdvEnabled(!advEnabled)}
        />
        <SwitchWithCounter
          title="Bias Test Cases"
          description="Number of Questions"
          count={biasCount}
          setCount={setBiasCount}
          isEnabled={biasEnabled}
          toggleSwitch={() => setBiasEnabled(!biasEnabled)}
        />
        <SwitchWithCounter
          title="Hallucination Test Cases"
          description="Number of Questions"
          count={hallCount}
          setCount={setHallCount}
          isEnabled={hallEnabled}
          toggleSwitch={() => setHallEnabled(!hallEnabled)}
        />
      </div>

      <div className="mt-6 bg-white p-4 shadow rounded">
        <h3 className="text-md font-semibold mb-2 text-gray-500 border-b pb-2">Upload Document</h3>
        <input
          type="file"
          multiple
          onChange={handleFilesChange}
          placeholder="no"
          className="block w-full text-sm text-white rounded-lg border-2  file:border-0 file:mr-4 file:py-2 file:px-4 file:text-sm file:font-semibold file:bg-gray-400 file:text-white file:cursor-pointer hover:file:bg-gray-600"
        />
        <div className="mt-4 flex gap-4">
          {files.length > 0 &&
            files.map((file, index) => (
              <li key={file.name + file.size} className="flex items-center justify-between p-2 border rounded bg-gray-50">
                <span className="truncate max-w-xs">{file.name}</span>
                <button
                  onClick={() => removeFile(index)}
                  className="ml-4 text-red-500 hover:text-red-700 font-bold"
                  aria-label={`Remove file ${file.name}`}
                  type="button"
                >
                  ×
                </button>
              </li>
            ))}
        </div>
      </div>
      <div className="flex justify-end mt-2">
        <button className="btn-primary" onClick={executeTest}>
          Execute Test
        </button>
      </div>

      <ModalWrapper isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <PreviousEvaluation files={outputFiles} />
      </ModalWrapper>
    </>
  );
};

export default TestCaseGenerator;
