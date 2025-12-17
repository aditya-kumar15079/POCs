import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { chatHistoryApi, chatStreamApi } from "@/services/api";

//createAsyncThunk([slice name]/[action name], callback function) for fetching messages
export const chatHistory = createAsyncThunk("chat/chatHistory", async (params, { rejectWithValue }) => {
  try {
    return await chatHistoryApi(params);
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const chatStream = createAsyncThunk("chat/chatStream", async (payload, { dispatch, rejectWithValue }) => {
  try {
    await chatStreamApi({
      payload,
      onChunk: (content) => {
        dispatch(appendBotMessage(content));
      },
      onError: (err) => {
        dispatch(setError(err));
      },
      onComplete: () => {
        dispatch(finalizeBotMessage());
      },
    });
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    messages: [],
    loading: false,
    error: null,
    sessionId: "",
    currentBotMessage: "",
    chatHistory: {
      chats: [],
      loading: false,
      error: null,
    },
  },
  reducers: {
    setMessages: (state, action) => {
      state.messages = action.payload;
    },
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    setSession: (state, action) => {
      state.sessionId = action.payload;
    },
    clearMessages: (state) => {
      state.messages = [];
      state.currentBotMessage = "";
      state.error = null;
    },
    appendBotMessage: (state, action) => {
      state.currentBotMessage += action.payload;
    },
    finalizeBotMessage: (state) => {
      if (state.currentBotMessage.trim()) {
        state.messages.push({ type: "bot", llm_response: state.currentBotMessage });
        state.currentBotMessage = "";
      }
      state.loading = false;
    },
    setError: (state, action) => {
      state.error = action.payload;
      state.loading = false;
    },
  },
  extraReducers: (builder) => {
    builder
      // chat history
      .addCase(chatHistory.pending, (state) => {
        state.chatHistory.loading = true;
        state.chatHistory.error = null;
      })
      .addCase(chatHistory.fulfilled, (state, action) => {
        state.chatHistory.loading = false;
        state.chatHistory.chats = action.payload;
      })
      .addCase(chatHistory.rejected, (state, action) => {
        state.chatHistory.loading = false;
        state.chatHistory.error = action.payload;
      })

      .addCase(chatStream.pending, (state) => {
        state.loading = true;
        state.currentBotMessage = "";
        state.error = null;
      })
      .addCase(chatStream.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || "Failed to fetch answer";
      });
  },
});

export const { setMessages, addMessage, setSession, clearMessages, appendBotMessage, finalizeBotMessage, setError } = chatSlice.actions;
export default chatSlice.reducer;