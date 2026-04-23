import { deserializeBin } from '../utils/serialize';

self.onmessage = async ({ data: { binData, language } }) => {
    self.postMessage(await deserializeBin(binData, language));
};
