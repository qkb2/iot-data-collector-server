import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getDevice, approveDevice } from "../api";
import type { DeviceDTO } from "../types";

export default function DeviceDetail() {
  const { id } = useParams();
  const [device, setDevice] = useState<DeviceDTO | null>(null);

  const refresh = useCallback(() => {
    if (id) {
      getDevice(id).then(setDevice).catch(console.error);
    }
  }, [id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  if (!device) return <div>Loading...</div>;

  return (
    <div className="space-y-6 p-4 bg-white rounded-xl shadow-sm">
      <h2 className="text-2xl font-bold tracking-tight">Device {device.id}</h2>

      {!device.approved && (
        <button
          onClick={() => approveDevice(device.id).then(refresh)}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg shadow transition-colors"
        >
          Approve Device
        </button>
      )}

      <div className="space-y-2">
        <h3 className="font-semibold text-xl">Sensors</h3>
        <ul className="list-disc pl-6 space-y-1">
          {device.sensors.map((s) => (
            <li key={s.id} className="text-gray-700">
              <span className="font-medium">{s.name}</span>{" "}
              <span className="text-gray-500">({s.type})</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
