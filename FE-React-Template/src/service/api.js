import axios from "axios";
// import axiosRetry from "axios-retry";

const apiBaseUrl = "https://your-base-url.com";

const axiosInstance = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// axiosInstance.interceptors.request.use(
//   async (config) => {
//     const token = getAccessToken(); // Fetch the latest token dynamically
//     if (token) {
//       config.headers["Authorization"] = `Bearer ${token}`;
//     }
//     return config;
//   },
//   (error) => {
//     return Promise.reject(error);
//   }
// );

// axiosInstance.interceptors.response.use(
//   (response) => {
//     console.log("response", response);
//     return response;
//   },
//   async (error) => {
//     console.error("error", error);
//     return Promise.reject(error);
//   }
// );

// axiosRetry(axiosInstance, {
//   retries: 3, // Number of retries
//   retryDelay: (retryCount) => {
//     return retryCount * 1000; // Time between retries (in ms)
//   },
//   retryCondition: (error) => {
//     return error.response && error.response.status === 401;
//   },
// });

const useAxios = () => {
  return axiosInstance;
};

export const api = {
  get: async (url, config = {}) => {
    try {
      const response = await axiosInstance.get(url, config);
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },

  post: async (url, data, config = {}) => {
    if (data === null) return;
    try {
      const response = await axiosInstance.post(url, data, config);
      return response.data;
    } catch (error) {
      handleError(error);
    }
  },
};

function handleError(error) {
  console.error("API error:", error);
  throw error?.response?.data || error;
}

export const METHODS = Object.freeze({
  GET: Symbol("get"),
  POST: Symbol("post"),
  PUT: Symbol("put"),
  DELETE: Symbol("delete"),
});

export default useAxios;
