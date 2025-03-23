import RealTimeChart from "../components/RealTimeChart";
import ControlPanel from "../components/ControlPanel";

export default function Home() {
  return (
    <div className="p-8 space-y-6">
      <RealTimeChart />
      <ControlPanel />
    </div>
  );
}
