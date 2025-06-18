import { configureStore } from "@reduxjs/toolkit";
import counterReducer from "./reducers/counterSlice.js"; //it is the default export form counterSlice, we can name it anything.

export const store = configureStore({
  reducer: {
    counter: counterReducer,
  },
});
