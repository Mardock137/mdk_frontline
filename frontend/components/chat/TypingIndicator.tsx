export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-sm ring-1 ring-gray-200">
        <span
          className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
          style={{ animationDelay: "0ms" }}
        />
        <span
          className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
          style={{ animationDelay: "150ms" }}
        />
        <span
          className="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
          style={{ animationDelay: "300ms" }}
        />
      </div>
    </div>
  );
}
