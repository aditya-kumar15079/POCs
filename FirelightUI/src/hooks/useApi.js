import { useState, useCallback, useEffect } from "react";
import { BASE_URL, BASE_URL_COMMONTAG } from "../utils/Constants";

const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  //   useEffect(() => {
  //       console.log(error);
  //   },[error])

  // GET request
  const GET = useCallback(async (endpoint, params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const query = new URLSearchParams(params).toString();
      const response = await fetch(`${BASE_URL}${endpoint}?${query}`, {
        method: "GET",
      });
      // if (!response.ok) throw new Error(`GET ${endpoint} failed`);
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message || "Something went wrong");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const GET_COMMONTAG = useCallback(async (endpoint, params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const query = new URLSearchParams(params).toString();
      const response = await fetch(`${BASE_URL_COMMONTAG}${endpoint}?${query}`, {
        method: "GET",
      });
      // if (!response.ok) throw new Error(`GET ${endpoint} failed`);
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message || "Something went wrong");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);


  // POST request
  const POST = useCallback(async (endpoint, body = {}, params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const query = new URLSearchParams(params).toString();
      const response = await fetch(
        `${BASE_URL}${endpoint}${query ? "?" + query : ""}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("authToken")}`,
          },
          body: JSON.stringify(body),
        }
      );
      // if (!response.ok) throw new Error(`POST ${endpoint} failed`);
      const data = await response.json();
      return data;
    } catch (err) {
      console.log(err);
      setError(err.message || "Something went wrong");
      return null;
      // return {
      //   id: "9ad50083-15b7-4057-b9f5-2e3d9072276b",
      //   user_id: "1",
      //   session_id: "1",
      //   user_input: "Generate a rule to make last name mandatory",
      //   text_response: "Here is your rule",
      //   xml_rule:
      //     '<block>\n  <if>\n    <condition>\n      <isnullorwhitespace>\n        <diget dataitemid="last name" />\n      </isnullorwhitespace>\n    </condition>\n    <postmessage dataitemid="last name">\n      <const value="Last name is required." />\n    </postmessage>\n    <else/>\n    <removemessage dataitemid="last name" />\n  </if>\n</block>',
      //   timestamp: "2025-07-22T13:52:50.735532+00:00",
      // };
    } finally {
      setLoading(false);
    }
  }, []);

  const POST_COMMONTAG = useCallback(async (endpoint, body = {}, params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const query = new URLSearchParams(params).toString();
      const response = await fetch(
        `${BASE_URL_COMMONTAG}${endpoint}${query ? "?" + query : ""}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("authToken")}`,
          },
          body: JSON.stringify(body),
        }
      );
      // if (!response.ok) throw new Error(`POST ${endpoint} failed`);
      const data = await response.json();
      return data;
    } catch (err) {
      console.log(err);
      setError(err.message || "Something went wrong");
      return null;
      // return {
      //   id: "9ad50083-15b7-4057-b9f5-2e3d9072276b",
      //   user_id: "1",
      //   session_id: "1",
      //   user_input: "Generate a rule to make last name mandatory",
      //   text_response: "Here is your rule",
      //   xml_rule:
      //     '<block>\n  <if>\n    <condition>\n      <isnullorwhitespace>\n        <diget dataitemid="last name" />\n      </isnullorwhitespace>\n    </condition>\n    <postmessage dataitemid="last name">\n      <const value="Last name is required." />\n    </postmessage>\n    <else/>\n    <removemessage dataitemid="last name" />\n  </if>\n</block>',
      //   timestamp: "2025-07-22T13:52:50.735532+00:00",
      // };
    } finally {
      setLoading(false);
    }
  }, []);

  return { GET, GET_COMMONTAG, POST_COMMONTAG, POST, loading, error };
};

export default useApi;
