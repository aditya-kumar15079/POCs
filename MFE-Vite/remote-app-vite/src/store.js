import { configureStore } from "@reduxjs/toolkit";
import chatbotReducer from "@/reducers/combinedReducer";


export const store = configureStore({
  reducer: {
    chatBot: chatbotReducer,
  },
});
