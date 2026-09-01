const axios = require('axios');
const client = axios.create({ headers: { 'Content-Type': 'application/json' } });

client.interceptors.request.use(req => {
  console.log(req.headers);
  return req;
});

client.post('http://example.com', new FormData(), {
  headers: { 'Content-Type': undefined }
}).catch(() => {});
