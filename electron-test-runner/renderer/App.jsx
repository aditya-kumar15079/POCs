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
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column */}
        <LeftPane />

        {/* Right Column */}
        <div className="md:col-span-2 p-4">
          <div className="flex justify-between items-center mb-4">
            <div className="flex space-x-4">
              {solutions
                ?.filter((sol) => sol.enabled)
                .map((sol, idx) => (
                  <button
                    type="button"
                    key={idx}
                    onClick={() => setCurrentTab(sol.id)}
                    className={`px-4 py-2 rounded font-semibold ${sol.id === currentTab ? "bg-blue-100 text-blue-600" : "text-gray-500"}`}
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
