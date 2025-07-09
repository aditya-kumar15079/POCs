import { configureStore } from "@reduxjs/toolkit";
import configReducer from "./reducers/configSlice";

export default configureStore({
  reducer: {
    config: configReducer,
  },
});
