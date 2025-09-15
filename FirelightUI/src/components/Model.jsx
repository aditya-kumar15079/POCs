import React, { use, useEffect, useState } from "react";
import FormContainer from "./FormContainer";
import Select from "./Select";
import Input from "./Input";
import useApi from "../hooks/useApi";
import ShimmerLoader from "./Shimmer";
import PaginatedSelect from "./PaginatedSelect";
import { BASE_URL, mockChatResponse } from "../utils/Constants";

const Model = ({ text, closeModal }) => {
  const [selectedCommanTag, setSelectedCommanTag] = useState("");
  const [commonTags, setCommonTags] = useState(null);
  const [fieldName, setFieldName] = useState("");
  const [apiError, setApiError] = useState(null);
  const { POST, POST_COMMONTAG, loading, error } = useApi();

  useEffect(() => {
    fetchData(text.trim());
  }, [POST]);

  useEffect(() => {
    setFieldName(text);
  }, [text]);

  const fetchData = async (payload) => {
    const data = BASE_URL ? await POST_COMMONTAG(
      "common-tag",
      { form_fields: [payload] },
      { code: "" }
    ) : await fetchStaticData(payload);
    if (data?.status === "SUCCESS") {
      setCommonTags(data?.payload[0]?.common_tags);
      setApiError(null);
    } else {
      setCommonTags(null);
      setApiError(data?.errors?.[0]?.error_message);
    }
  };

  const fetchStaticData = async (payload) => {
    const data = mockChatResponse[1].common_tags_selection_data[0]
    return data
  };

  const handleKeyUp = (event) => {
    if (event.key === "Enter") {
      setCommonTags(null);
      setApiError(null);
      fetchData(fieldName.trim());
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/63">
      <div className="flex-col bg-white rounded-xl shadow-lg w-120">
        <FormContainer title="Text Box Properties" border="none">
          <Input
            title="Field Name"
            type="text"
            width={4}
            value={fieldName}
            onChange={(e) => setFieldName(e.target.value)}
            onBlur={closeModal}
            onKeyUp={handleKeyUp}
            error={apiError}
          />
          {commonTags ? <PaginatedSelect
            label="Select Common Tag"
            name="common_tag"
            width={4}
            value={selectedCommanTag}
            onChange={(e) => setSelectedCommanTag(e.target.value)}
            options={commonTags.map((tag) => ({
              value: tag.commontag,
              label: tag.commontag,
            }))}
          />: <div><span className="text-sm font-semi text-black">Select Common Tag</span><ShimmerLoader width="380px" height="38px" className="mt-2" error={apiError}/></div> }
        </FormContainer>
        <div className="flex justify-end gap-2 p-4">
          <button
            onClick={() => closeModal()}
            className="flex px-4 h-12 bg-hexblue text-white rounded cursor-pointer items-center"
          >
            Cancel
          </button>
          <button
            onClick={() => closeModal()}
            className="flex px-4 h-12 bg-hexblue text-white rounded cursor-pointer items-center"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default Model;
