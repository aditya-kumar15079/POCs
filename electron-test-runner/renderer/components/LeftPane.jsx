import { useDispatch, useSelector } from "react-redux";
import { DropdownSelect } from "./DropdownSelect";
import { useState } from "react";
import { selectIteration, selectProject, submitSolutions } from "../reducers/configSlice";

const LeftPane = () => {
  const [selSolutions, setSelSolutions] = useState([true, true, true]);

  const solutions = useSelector((state) => state.config.solutions);
  const projects = useSelector((state) => state.config.projects);
  const iterations = useSelector((state) => state.config.iteration);

  const dispatch = useDispatch();
  const handleSubmit = () => {
    // window.api.runLLMJudge();
    const updatedSolutions = solutions.map((sol, idx) => ({ ...sol, enabled: selSolutions[idx] }));
    dispatch(submitSolutions(updatedSolutions));
  };

  const handleCheckedChange = (index) => {
    const updated = selSolutions.map((val, idx) => (idx === index ? !val : val));
    setSelSolutions(updated);
  };

  const onDropDownSelect = (action) => {
    return (index) => {
      action(index);
    };
  };

  // const onProjectSelect = (index) => {
  //   dispatch(selectProject(index));
  // };
  // const onProjectSelect = (index) => {
  //   dispatch(selectProject(index));
  // };

  return (
    <>
      <div className="bg-white p-4 shadow rounded">
        <h2 className="text-lg font-semibold mb-4 text-gray-500">Project Configuration</h2>
        <DropdownSelect label="Project Name" options={projects} onSelected={onDropDownSelect(selectIteration)} />
        <DropdownSelect label="Iteration Number" options={iterations} onSelected={onDropDownSelect(selectIteration)} />

        <div className="mt-6">
          <h3 className="text-md font-semibold mb-2">Solutions</h3>
          {solutions.map((solution, idx) => (
            <div key={idx} className="flex items-center space-x-2 mb-2">
              <input
                type="checkbox"
                checked={selSolutions?.[idx]}
                onChange={() => handleCheckedChange(idx)}
                className="form-checkbox h-4 w-4 text-blue-600"
              />
              <label onClick={() => handleCheckedChange(idx)} className="text-gray-700 text-sm">
                {solution?.name}
              </label>
            </div>
          ))}
        </div>

        <div className="mt-4 flex space-x-2">
          <button className="bg-gray-200 px-4 py-2 rounded">Reset</button>
          <button className="bg-blue-600 text-white px-4 py-2 rounded" onClick={handleSubmit}>
            Submit
          </button>
        </div>
      </div>
    </>
  );
};

export default LeftPane;
