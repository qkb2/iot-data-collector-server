export interface SensorDTO {
  id: number;
  name: string;
  type: string;
}

export interface DeviceDTO {
  id: string;
  approved: boolean;
  sensors: SensorDTO[];
  sensor_count: number;
}
