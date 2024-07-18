//A hack within pipedream env to install ffmpeg (doesn't work with other install methods for some reason)
import fs from 'fs';
import https from 'https';
import { exec } from 'child_process';
import { promisify } from 'util'; // Import promisify
import ffmpegInstaller from '@ffmpeg-installer/ffmpeg';

const ffmpegPath = ffmpegInstaller.path;
export default defineComponent({
  async run({ steps, $ }) {
    // Return data to use it in future steps
    return ffmpegPath
  },
})