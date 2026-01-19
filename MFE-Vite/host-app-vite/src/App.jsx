import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { decrement, increment } from "./reducers/counterSlice";
import Loader from "./components/common/Loader";
import CoachMaci from "remoteApp/ChatRoot";

function App() {
  // const [count, setCount] = useState(0);
  const count = useSelector((state) => state?.chatBot?.counter.value);
  const dispatch = useDispatch();

  const authToken =
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTI5MjM1LTAwMjI2MjAiLCJuYW1lIjoiQWRpdHlhIEt1bWFyIiwiZW1haWwiOiJhZGl0eWEua3VtYXIyQGhhcHBpZXN0bWluZHMuY29tIiwiY291cnNlIjoiQ29tcFRJQSBBKyIsImV4cCI6MTc2ODQwNTk2MCwidG9rZW5faWQiOiJjNmZjMWMxYS1iNGY0LTRmMTktYTMwYi02ZTU5Njc3OWU5ZTcifQ._-004ovpAHC9WQsOkhm5vCDrI8XxxeOO9eATkH0pfTY";

  return (
    <div className="flex p-4">
      <div className="flex-3 bg-gray-100"></div>
      <div className="flex-1 p-1">
        {/* remote component */ }
        <CoachMaci authToken={authToken} courseName="Comptia A+" userName="JohnDoe" moreDetails={{}} mode="my-aci" />
      </div>
    </div>
  );
}

export default App;
