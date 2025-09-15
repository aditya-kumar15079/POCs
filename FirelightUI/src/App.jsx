import { useEffect, useState } from "react";
import "./App.css";
import Input from "./components/Input";
import FormContainer from "./components/FormContainer";
import Model from "./components/Model";
import useApi from "./hooks/useApi";
import Chatbot from "./components/Chatbot";
import { BASE_URL, } from "./utils/Constants";

function App() {
  const [selectedId, setSelectedId] = useState(null);
  const [isModelShowing, toggleModelShowing] = useState(false);
    const { GET, GET_COMMONTAG, loading, error } = useApi();

  const data = [
    { id: 1, title: "Financial Institution Name", width: "12" },
    { id: 2, title: "Account Holder First Name", width: "4" },
    { id: 3, title: "Middle Name", width: "4" },
    { id: 4, title: "Last Name", width: "4" },
    { id: 5, title: "Address", width: "4" },
    { id: 6, title: "City", width: "4" },
    { id: 7, title: "State", width: "4" },
    { id: 8, title: "Zip Code", width: "6" },
  ]

  useEffect(() => {
      BASE_URL && (async () => {
        const data = await GET_COMMONTAG("generate-token", { 'code': "" });
        if (data) {
          localStorage.setItem("authToken", data?.token);
        }
      })();
    }, [GET_COMMONTAG]);

  const handleCardClick = (id) => {
    setSelectedId((prev) => (prev === id ? null : id));
  };

  const handleShowModel = (event) => {
    if(event?.stopPropagation) event.stopPropagation();
    toggleModelShowing(!isModelShowing);
  };

  const closeModal = () => {
    toggleModelShowing(false);
  };

  return (
    <div style={{ width: "1280px" }}>
      <FormContainer title="ACH Payment">
        {data?.map(({id, title, width}) => (
          <Input
            key={id}
            title={title}
            placeholder=""
            type="text"
            width={width}
            id={id}
            selected={id === selectedId}
            onClick={() => handleCardClick(id)}
            showPopUp={handleShowModel}
          />
        ))}
      </FormContainer>
      {isModelShowing && <Model closeModal={closeModal} text={data[selectedId-1]?.title} />}
      <Chatbot />
    </div>
  );
}

export default App;
