import { useEffect, useState } from "react";
import api, { METHODS } from "../service/api";

const useApi = (url, requestData, method, config) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const request = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = method === METHODS.POST ? await api.post(url, requestData, config) : await api.get(url, config);
        setData(response);
        return response;
      } catch (err) {
        setError(err);
        setData(null);
        console.error("API Error:", err);
      } finally {
        setLoading(false);
      }
    };
    request();
  }, [requestData]);

  return { data, loading, error };
};

export default useApi;
