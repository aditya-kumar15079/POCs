import { configureStore, createSlice } from "@reduxjs/toolkit";

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    messages: [],
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
  },
});

export const { addMessage } = chatSlice.actions;

const store = configureStore({
  reducer: {
    chat: chatSlice.reducer,
  },
});

export default store;
