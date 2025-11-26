import { useEffect, useState } from "react";
import { getDevices } from "../api";
import type { DeviceDTO } from "../types";
import { Link } from "react-router-dom";

export default function Devices() {
  const [devices, setDevices] = useState<DeviceDTO[]>([]);

  useEffect(() => {
    getDevices().then(setDevices).catch(console.error);
  }, []);

  return (
    <div className="space-y-4">
      {devices.map((d) => (
        <Link key={d.id} to={`/device/${d.id}`}>
          <div className="p-4 border rounded-xl shadow hover:bg-gray-50">
            <div className="font-semibold">{d.id}</div>
            <div className="text-sm text-gray-600">
              Sensors: {d.sensor_count}
            </div>
            {!d.approved && (
              <div className="text-red-600">Pending approval</div>
            )}
          </div>
        </Link>
      ))}
    </div>
  );
}
