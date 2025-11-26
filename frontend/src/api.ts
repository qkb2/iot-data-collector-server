import type { DeviceDTO } from "./types";

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(path, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export const getDevices = () => api<DeviceDTO[]>("/api/frontend/devices");
export const getDevice = (id: string) =>
  api<DeviceDTO>(`/api/frontend/devices/${id}`);
export const approveDevice = (id: string) =>
  api<{ success: boolean }>(`/api/frontend/devices/${id}/approve`, {
    method: "POST",
  });
