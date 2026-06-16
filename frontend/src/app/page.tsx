import { BandExplorer } from "@/components/BandExplorer";

export default function Home() {
  return (
    <main className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Solar Cost Explorer</h1>
        <p className="text-gray-600 mt-2">
          Browse solar installation cost benchmarks ($/W) by system size, panel tier, location,
          and installer type. P90 data is visible to authenticated users only.
        </p>
      </div>
      <BandExplorer />
    </main>
  );
}
