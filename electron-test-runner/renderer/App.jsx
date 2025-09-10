import React, { useEffect } from "react";
import TestCaseGenerator from "./components/TestCaseGenerator";
import LeftPane from "./components/LeftPane";
import EvaluationForm from "./components/EvaluationForm";
import { useSelector } from "react-redux";

const App = () => {
  const [currentTab, setCurrentTab] = React.useState(101);
  // const llmResponseMetrics = ["Accuracy", "Coherence", "Relevance", "Faithfulness", "Bias", "Toxicity"];
  // const genAICompassMetrics = ["BLEU Score", "ROUGE Score", "Meteor Score", "Bert Score", "Accuracy", "Coherence", "Toxicity"];
  const solutions = useSelector((state) => state.config.solutions);

  // useEffect(() => {
  //   (async () => {
  //     const path = await window.api.getParentPath();
  //     console.log("window.api.getParentPath()", path);
  //   })();
  // }, []);

  const getTabComponent = () => {
    switch (currentTab) {
      case 101:
        return <TestCaseGenerator />;
      case 102:
        return <EvaluationForm id={currentTab} />;
      case 103:
        return <EvaluationForm id={currentTab} />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-1">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-1">
        {/* Left Column */}
        <LeftPane />

        {/* Right Column */}
        <div className="md:col-span-3 p-2 bg-white shadow rounded max-w-5xl">
          <div className="flex justify-between items-center">
            <div className="flex bg-gray-100">
              {solutions
                ?.filter((sol) => sol.enabled)
                .map((sol, idx) => (
                  <button
                    type="button"
                    key={idx}
                    onClick={() => setCurrentTab(sol.id)}
                    className={`px-4 py-2 rounded font-semibold cursor-pointer border border-gray-300 ${
                      sol.id === currentTab ? "bg-white text-blue-600 border-b-0" : "text-gray-500"
                    }`}
                  >
                    {sol.name}
                  </button>
                ))}
            </div>
          </div>

          {getTabComponent()}
        </div>
      </div>
    </div>
  );
};

export default App;
