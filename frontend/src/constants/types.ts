export interface AudioDataResponse {
  num_frames: number;
  num_channels: number;
  sample_rate: number;
  duration: number;
}

export interface QueryIdResponse {
  uuid: string;
  name: string;
  source: string;
  created: Date;
  available: boolean;
  data: AudioDataResponse | null;
}

export interface QueryIdsResponse {
  infos: QueryIdResponse[];
}
