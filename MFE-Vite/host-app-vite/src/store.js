import { configureStore } from "@reduxjs/toolkit";
import chatReducer from "@/reducers/chatSlice";
import counterReducer from "@/reducers/counterSlice";
import chatbotReducer from "remoteApp/chatbotReducer";


export const store = configureStore({
  reducer: {
    counter: counterReducer,
    chat: chatReducer,
    coachMaci: chatbotReducer,  // remote reducer
  },
});
