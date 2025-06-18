import { useState } from "react";
import "./App.css";
import { useDispatch, useSelector } from "react-redux";
import { decrement, increment } from "./reducers/counterSlice";
import Spinner from "./loading/Spinner";
import Loader from "./loading/Loader";

function App() {
  // const [count, setCount] = useState(0);
  const count = useSelector((state) => state.counter.value);
  const dispatch = useDispatch();

  return (
    <>
      <h1 className="text-3xl font-bold">Vite + React</h1>
      <div className="card">
        <h2>Counter: {count}</h2>
        <button className="primary-button" onClick={() => dispatch(increment())}>
          increment
        </button>
        <button className="secondary-button mx-4" onClick={() => dispatch(decrement())}>
          decrement
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
    </>
  );
}

export default App;
