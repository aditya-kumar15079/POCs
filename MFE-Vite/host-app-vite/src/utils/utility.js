import dayjs from "dayjs";
import customParseFormat from "dayjs/plugin/customParseFormat.js";
import utc from "dayjs/plugin/utc.js";

dayjs.extend(customParseFormat);
dayjs.extend(utc);

// Define all possible input formats you expect
const SUPPORTED_FORMATS = ["DDMMYYYY HH:mm:ss", "DD/MM/YYYY HH:mm:ss", "YYYY-MM-DDTHH:mm:ss", "YYYY-MM-DD"];

// Utility function
export const formatDate = (input, targetFormat = "MM/DD/YYYY hh:mm:ss A") => {
  if (dayjs(input).isValid()) {
    return dayjs(input).format(targetFormat);
  }

  for (const fmt of SUPPORTED_FORMATS) {
    const parsed = dayjs(input, fmt, true); // strict parsing
    if (parsed.isValid()) {
      return parsed.format(targetFormat);
    }
  }
  return "Invalid date"; // fallback
};

export const dateComparator =
  (datekey, ascending = true) =>
  (a, b) => {
    const dateA = formatDate(a?.[datekey]);
    const dateB = formatDate(b?.[datekey]);
    return ascending ? new Date(dateA) - new Date(dateB) : new Date(dateB) - new Date(dateA);
  };

export const toDisplayFormat = (dateStr) => {
  if (!dateStr) return "";
  if (dateStr.split("-").length !== 3) return dateStr;

  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const [year, month, day] = dateStr.split("-");
  return `${day}-${months[parseInt(month, 10) - 1]}-${year}`;
};
