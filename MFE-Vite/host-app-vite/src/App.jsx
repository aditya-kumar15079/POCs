import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { decrement, increment } from "./reducers/counterSlice";
import Loader from "./components/common/Loader";
import Chatbot from "chatbot/ChatRoot";

function App() {
  // const [count, setCount] = useState(0);
  const count = useSelector((state) => state.counter.value);
  const dispatch = useDispatch();

  return (
    <>
      <h1 className="text-sm">React + Tailwind Template</h1>
      <div className="flex flex-col gap-2">
        <div className="flex items-center">
          <label className="mr-10 font-bold">Buttons:</label>
          <button type="button" className="primary-button" onClick={() => dispatch(increment())}>
            increment
          </button>
          <button type="button" className="secondary-button mx-4" onClick={() => dispatch(decrement())}>
            decrement
          </button>
          <label>Counter: {count}</label>
        </div>

        <div className="flex items-center">
          <label className="mr-10 font-bold">Disabled:</label>
          <button type="button" className="primary-button" disabled={true}>
            Fetch data
          </button>
        </div>

        <div className="flex items-center">
          <label className="mr-10 font-bold">Loader:</label>
          <Loader />
        </div>
      </div>
      <Chatbot />
    </>
  );
}

export default App;
