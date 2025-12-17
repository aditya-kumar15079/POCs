import { MapPin } from "lucide-react";

const TopBar = () => {

  const handleLocationClick = () => {
    console.log("Location icon clicked");
  };

  return (
    <header className="flex items-center justify-between p-4 border-b border-gray-300 bg-bg shadow-sm">
      <h1 className="text-lg font-semibold font-[goldenbook]">Coco Republic</h1>

      <button onClick={handleLocationClick} className="p-2 hover:bg-gray-300 rounded-full" title="Select your location">
        <MapPin size={22} />
      </button>
    </header>
  );
}
export default TopBar;