import { combineReducers } from "@reduxjs/toolkit";
import counterReducer from "@/reducer/counterSlice";
import chatReducer from "@/reducer/chatSlice";

const chatbotReducer = combineReducers({
  counter: counterReducer,
  chat: chatReducer,
});

export default chatbotReducer;
