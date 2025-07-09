import { createSlice } from "@reduxjs/toolkit";

export const configSlice = createSlice({
  name: "config",
  initialState: {
    projects: ["Project 1", "Project 2", "Project 2"],
    selProjectIndex: 0,
    iteration: ["Iteration 1", "Iteration 2", "Iteration 3"],
    selIterationIndex: 0,
    solutions: [
      { id: 101, name: "Test Foundry", enabled: true },
      { id: 102, name: "GENAI  ResponseQuality Framework", enabled: true },
      { id: 103, name: "GENAI Compass", enabled: true },
    ],
  },
  reducers: {
    selectProject: (state, action) => {
      state.selProjectIndex = action.payload;
    },
    selectIteration: (state, action) => {
      state.selIterationIndex = action.payload;
    },
    selectSolutions: (state, action) => {
      if (action?.payload?.index < state.solutions?.length) {
        state.solutions[action.payload.index].enabled = action.payload?.value;
      }
    },
    submitSolutions: (state, action) => {
      state.solutions = action.payload;
    },
  },
});

export const { selectProject, selectIteration, selectSolutions, submitSolutions } = configSlice.actions;

export default configSlice.reducer;
