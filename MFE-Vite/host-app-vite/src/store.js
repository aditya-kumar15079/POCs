import { configureStore } from "@reduxjs/toolkit";
import chatReducer from "@/reducers/chatSlice";
import counterReducer from "@/reducers/counterSlice";


export const store = configureStore({
  reducer: {
    counter: counterReducer,
    chat: chatReducer,
  },
});
