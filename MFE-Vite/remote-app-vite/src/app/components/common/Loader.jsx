
const Loader = () => {
  return (
    <div className="flex gap-4 items-center justify-center min-h-screen bg-gray-50">
      <div className="h-12 w-12 rounded bg-gray-300 animate-bounce [animation-delay:0ms]" />
      <div className="h-12 w-12 rounded bg-gray-300 animate-bounce [animation-delay:200ms]" />
      <div className="h-12 w-12 rounded bg-gray-300 animate-bounce [animation-delay:400ms]" />
    </div>
  );
};

export default Loader;
