import React, { useEffect, useState, useRef } from "react";
import XmlViewer from "./XmlViewer";
import Spinner from "./Spinner";
import { BASE_URL, mockChatResponse } from "../utils/Constants";
import useApi from "../hooks/useApi";
import ExtractedKeywords from "./ExtractedKeywords";
import { TriangleAlert } from "lucide-react";

const MessageCard = ({
  message: {
    role,
    text,
    text_response,
    xml_rule,
    extracted_keywords,
    sessionId="0",
    loading,
    clicked,
  } = {},
  setNewSession
}) => {
  const { POST, loading: apiLoading } = useApi();
  const [showExtractadKeywords, setShowExtractadKeywords] = useState(false);
  const [commonTagsSelectionData, setCommonTagsSelectionData] = useState([]);
  const [selectedCommanTags, setSelectedCommanTags] = useState([]);
  const [showFinalXmlRule, setShowFinalXmlRule] = useState(false);
  const [finalXmlRule, setFinalXmlRule] = useState(null);
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    if (xml_rule && extracted_keywords?.length) {
      handleCommontags();
    }
  }, [xml_rule, extracted_keywords]);

  const handleCommontags = async () => {
    const { common_tags_selection_data } = BASE_URL
      ? await fetchCommonTags()
      : await fetchStaticCommonTags();
    setCommonTagsSelectionData(common_tags_selection_data);
  };

  const fetchCommonTags = async () => {
    const data = await POST("get-and-select-common-tags", {
      user_id: "1",
      session_id: sessionId,
      xml_rule,
      extracted_keywords,
    });
    return data;
  };

  const fetchStaticCommonTags = async (payload) => {
    return mockChatResponse[1];
  };

  // useEffect(() => {
  //   if (selectedCommanTags.length > 0) {
  //     const { final_xml_rule } = BASE_URL ? await fetchFinalXmlRule(selectedCommanTags) : await fetchStaticFinalXmlRule();
  //     setFinalXmlRule(final_xml_rule);
  //   }
  // }, [selectedCommanTags]);

  const fetchFinalXmlRule = async (selectedCommanTags) => {
    const data = await POST("replace-fields-with-common-tags/", {
      user_id: "1",
      session_id: sessionId,
      xml_rule,
      selected_tags: selectedCommanTags,
    });
    return data;
  };

  const fetchStaticFinalXmlRule = async () => {
    return mockChatResponse[2];
  };

  const handleConfirmSelection = async () => {
    setShowFinalXmlRule(true);
    if (selectedCommanTags.length > 0) {
      const { final_xml_rule, disable_input_box } = BASE_URL
        ? await fetchFinalXmlRule(selectedCommanTags)
        : await fetchStaticFinalXmlRule();
      setFinalXmlRule(final_xml_rule);
      if(disable_input_box){
        setNewSession(true);
      }
    }
  };

  useEffect(() => {
    if (clicked?.type === "yes") {
      setShowExtractadKeywords(true);
    }
    if (clicked?.type === "confirm") {
      handleConfirmSelection();
    }
  }, [clicked]);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [finalXmlRule, commonTagsSelectionData, showExtractadKeywords]);
  

  const getmessageCard = () => {
    if (role === "user") {
      return (
        <div className="mt-2 px-4 py-2 border border-gray-300 border-b-0 rounded-lg rounded-b-none bg-gray-200">
          <h4 className="font-semibold text-gray-800">{text}</h4>
        </div>
      );
    }
    if (role === "bot") {
      return (
        <>
          <div className="p-4 border border-gray-300 border-t-0 rounded-lg rounded-t-none bg-white">
            {loading ? (
              <Spinner
                message=""
                dot="."
                spinner={false}
              />
            ) : (
              <>
                <p className="text-gray-700 text-sm">{text_response}</p>
                {xml_rule && <XmlViewer xml={xml_rule} />}
              </>
            )}
          </div>
          {extracted_keywords?.length > 0 && (
            <div className="flex ml-4  my-4 items-center">
              <p className="text-gray-700 text-xs">
                Found {extracted_keywords.length} form field
                {extracted_keywords.length > 1 ? "s" : ""}. Would you like to
                select common tags for them?
              </p>
              {!showExtractadKeywords && (
                <button
                  className="bg-hexblue text-white text-sm rounded px-2 py-1 ml-1 hover:bg-blue-800"
                  onClick={() => setShowExtractadKeywords(true)}
                >
                  Yes
                </button>
              )}
            </div>
          )}
          {showExtractadKeywords && (
            <>
              <div className="mt-2 px-4 py-2 border border-gray-300 border-b-0 rounded-lg rounded-b-none bg-gray-200">
                <h4 className="font-semibold text-gray-800">
                  {clicked?.text || "Yes"}
                </h4>
              </div>
              <div
                className={`p-4 ${
                  showFinalXmlRule ? "" : "mb-40"
                } border border-gray-300 border-t-0 rounded-lg rounded-t-none bg-white`}
              >
                <ExtractedKeywords
                  data={commonTagsSelectionData}
                  keywords={extracted_keywords}
                  selectedCommanTags={selectedCommanTags}
                  setSelectedCommanTags={setSelectedCommanTags}
                  confirmSelection={() => handleConfirmSelection()}
                />
              </div>
              {showFinalXmlRule && extracted_keywords.length > 2 && (
                <div className="flex my-3 ml-2 text-gray-700 text-xs items-center">
                  <TriangleAlert color="#b19c35" />{" "}
                  <p className="ml-2">
                    Multiple form fields detected, we suggest to reduce the
                    complexity of the query
                  </p>
                </div>
              )}
            </>
          )}
          {showFinalXmlRule && (
            <div className="mt-4 p-4 border border-gray-300 rounded-lg bg-white">
              {finalXmlRule ? (
                <>
                  <p className="text-gray-700 text-sm">
                    Based on your above selection here is the final xml rule
                  </p>
                  {xml_rule && <XmlViewer xml={finalXmlRule} />}
                </>
              ) : (
                <Spinner
                  message="Creating final xml rule"
                  dot="."
                  spinner={false}
                />
              )}
            </div>
          )}
          <div ref={endOfMessagesRef} />
        </>
      );
    }
    if (role === "welcome") {
      return (
        <div className="p-4">
          <p className="text-gray-700 font-semibold text-sm">{text}</p>
        </div>
      );
    }
  };

  return getmessageCard();
};

export default MessageCard;
