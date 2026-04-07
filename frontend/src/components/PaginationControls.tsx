interface PageInfo {
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  endCursor?: string | null;
}

interface PaginationControlsProps {
  pageInfo?: PageInfo;
  onNext: () => void;
  onPrev: () => void;
}

export function PaginationControls({ pageInfo, onNext, onPrev }: PaginationControlsProps) {
  if (!pageInfo) return null;

  return (
    <div className="flex items-center justify-between">
      <button
        onClick={onPrev}
        disabled={!pageInfo.hasPreviousPage}
        className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        Previous
      </button>
      <button
        onClick={onNext}
        disabled={!pageInfo.hasNextPage}
        className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        Next
      </button>
    </div>
  );
}
