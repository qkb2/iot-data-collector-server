import { useEffect, useState, useCallback } from "react";
import { getDevices } from "../api";
import type { DeviceDTO } from "../types";
import { Link } from "react-router-dom";

export default function Devices() {
  const [devices, setDevices] = useState<DeviceDTO[]>([]);

  const refreshDevices = useCallback(() => {
    getDevices().then(setDevices).catch(console.error);
  }, []);

  useEffect(() => {
    refreshDevices();
    const interval = setInterval(refreshDevices, 10_000);
    return () => clearInterval(interval);
  }, [refreshDevices]);

  return (
    <div className="space-y-4">
      {devices.map((d) => (
        <Link key={d.id} to={`/device/${d.id}`}>
          <div className="p-4 border rounded-xl shadow-sm hover:shadow-md transition-shadow bg-white">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold text-lg">{d.id}</div>
                <div className="text-sm text-gray-600">
                  Sensors: {d.sensor_count}
                </div>
              </div>
              {!d.approved && (
                <div className="text-red-600 font-medium">Pending</div>
              )}
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
