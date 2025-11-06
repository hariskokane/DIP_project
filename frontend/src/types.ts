export interface BottleData {
  'Bottle Number': number;
  Cap: string;
  Label: string;
  Plastic: string;
  Status: string;
  Day: string;
  Date: string;
  Time: string;
  play_alert?: boolean;
}

export interface Stats {
  total: number;
  defective: number;
  nonDefective: number;
  defectRate: number;
}
