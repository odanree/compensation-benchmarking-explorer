export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-16">
      <div className="animate-spin rounded-full h-10 w-10 border-2 border-gray-200 border-t-blue-600" />
    </div>
  );
}
