import { deserializeBin } from '../utils/serialize';

self.onmessage = ({ data: { binData, language } }) => {
    self.postMessage(deserializeBin(binData, language));
};
