import { PlansTable } from "@/components/plans-table";

export const Plan = () => {
  return (
    <>
      <div className="p-4">
        <img src="http://localhost:8000/image" crossOrigin="use-credentials" />
        <PlansTable />
      </div>
    </>
  );
};
