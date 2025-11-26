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
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Device {device.id}</h2>

      {!device.approved && (
        <button
          onClick={() => approveDevice(device.id).then(refresh)}
          className="px-4 py-2 bg-green-600 text-white rounded"
        >
          Approve Device
        </button>
      )}

      <h3 className="font-semibold">Sensors</h3>
      <ul className="list-disc pl-6">
        {device.sensors.map((s) => (
          <li key={s.id}>
            {s.name} ({s.type})
          </li>
        ))}
      </ul>
    </div>
  );
}
