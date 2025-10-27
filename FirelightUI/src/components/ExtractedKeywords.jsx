import React, { useEffect, useState } from "react";
import ShimmerLoader from "./Shimmer";
import PaginatedSelect from "./PaginatedSelect";

const ExtractedKeywords = ({
  data,
  keywords,
  selectedCommanTags,
  setSelectedCommanTags,
  confirmSelection
}) => {

  const [confirm, setConfirm] = useState(false)

  const handleConfirm = () => {
    setConfirm(true)
    confirmSelection()
  }

  return (
    <div className="h-full">
      <p className="text-sm font-semi text-black">
        Select common tags for below form fields (whichever is
        applicable)
      </p>
      <div className="pl-1 gap-2">
        {keywords?.map((item, index) => (
          <div key={index}>
            {data?.[index]?.common_tags ? (
              <PaginatedSelect
                label={item}
                name={item}
                width={5}
                value={selectedCommanTags.find((tag) => tag.input === item)?.selected_common_tag}
                onChange={(e) => setSelectedCommanTags(prev => [...prev.filter(tag => tag.input !== item), {input: item, selected_common_tag: e.target.value}])}
                options={data?.[index]?.common_tags?.map((tag) => ({
                  value: tag.commontag,
                  label: tag.commontag,
                }))}
                view="row"
                enabled={!confirm}
              />
            ) : (
              <div className="flex w-125/200">
                <span className="text-sm font-semi text-black w-1/2">
                  {item}
                </span>
                <ShimmerLoader
                  width="200px"
                  height="30px"
                  className="w-1/2"
                />
              </div>
            )}
          </div>
        ))}
      </div>
      {selectedCommanTags?.length > 0 && <button className="bg-hexblue text-white text-sm rounded px-2 py-1 ml-1 my-2 hover:bg-blue-800" onClick={handleConfirm}>Confirm</button>}
    </div>
  );
};

export default ExtractedKeywords;
