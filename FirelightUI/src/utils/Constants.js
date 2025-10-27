export const BASE_URL = "https://fnw10sjl-8000.inc1.devtunnels.ms/";
export const BASE_URL_COMMONTAG = "https://flt-dev-genai-ncu-func02-dsb3gbb8c2d4fnag.northcentralus-01.azurewebsites.net/api/";

export const mockChatResponse = [
  {
    id: "4fa6e7f1-e72d-419b-9903-78c19f44714f",
    user_id: "123242423",
    session_id: "423423432",
    user_input:
      "Give me a rule to contatenate the first name and last name to form the full name",
    text_response: null,
    xml_rule:
      '<block>\n    <diset dataitemid="full name">\n        <concat>\n            <diget dataitemid="first name" type="String" />\n            <const value=" " />\n            <diget dataitemid="last name" type="String" />\n        </concat>\n    </diset>\n</block>',
    extracted_keywords: ["first name", "last name", "full name large text"],
    timestamp: "2025-07-23T19:09:02.246134+00:00",
  },
  {
    user_id: "123242423",
    session_id: "423423432",
    common_tags_selection_data: [
      {
        input: "first name",
        common_tags: [
          {
            commontag: "Spouse_FirstName",
            score: 0.67541736,
          },
          {
            commontag: "Party1_FirstName",
            score: 0.67249554,
          },
          {
            commontag: "Party5_FirstName",
            score: 0.6680333,
          },
          {
            commontag: "Minor_FirstName",
            score: 0.6648271,
          },
          {
            commontag: "Party4_FirstName",
            score: 0.6637903,
          },
          {
            commontag: "Party3_FirstName",
            score: 0.6620458,
          },
          {
            commontag: "Guardian_FirstName",
            score: 0.6583838,
          },
          {
            commontag: "TrustedContact1_FirstName",
            score: 0.658206,
          },
          {
            commontag: "Owner_FirstName",
            score: 0.6581788,
          },
          {
            commontag: "SpouseBeneficiary_FirstName",
            score: 0.65759766,
          },
        ],
        status: "SUCCESS",
      },
      {
        input: "last name",
        common_tags: [
          {
            commontag: "Minor_LastName",
            score: 0.67777294,
          },
          {
            commontag: "Spouse_LastName",
            score: 0.65693235,
          },
          {
            commontag: "Party1_LastName",
            score: 0.6537842,
          },
          {
            commontag: "Payor_LastName",
            score: 0.65172505,
          },
          {
            commontag: "Party2_LastName",
            score: 0.65106845,
          },
          {
            commontag: "Party3_LastName",
            score: 0.6505774,
          },
          {
            commontag: "Party4_LastName",
            score: 0.64920485,
          },
          {
            commontag: "ContingentOwner_LastName",
            score: 0.6484168,
          },
          {
            commontag: "Custodian2_LastName",
            score: 0.64823556,
          },
          {
            commontag: "Party5_LastName",
            score: 0.6481683,
          },
        ],
      },
      {
        input: "full name",
        common_tags: [
          {
            commontag: "Party4_FullName",
            score: 0.64248127,
          },
          {
            commontag: "AdditionalAgent4_FullName",
            score: 0.6356186,
          },
          {
            commontag: "Agent_FullName",
            score: 0.6314618,
          },
          {
            commontag: "Party5_FullName",
            score: 0.63139194,
          },
          {
            commontag: "AdditionalAgent5_FullName",
            score: 0.62995565,
          },
          {
            commontag: "AdditionalAgent1_FullName",
            score: 0.6296356,
          },
          {
            commontag: "Party1_FullName",
            score: 0.62951714,
          },
        ],
      },
    ],
    xml_rule:
      '<block>\n    <diset dataitemid="full name">\n        <concat>\n            <diget dataitemid="first name" type="String" />\n            <const value=" " />\n            <diget dataitemid="last name" type="String" />\n        </concat>\n    </diset>\n</block>',
    message: "Common tags fetched successfully.",
  },
  {
    user_id: "123242423",
    session_id: "423423432",
    final_xml_rule:
      '<block>\n  <diset dataitemid="Party5_FullName">\n    <concat>\n      <diget dataitemid="Party5_FirstName" type="String"/>\n      <const value=" "/>\n      <diget dataitemid="Party5_LastName" type="String"/>\n    </concat>\n  </diset>\n</block>\n',
    disable_input_box: true,
  },
];
