const axios = require('axios');
const FormData = require('form-data');
const client = axios.create({ headers: { 'Content-Type': 'application/json' } });

client.interceptors.request.use(req => {
  console.log(req.headers);
  return req;
});

const fd = new FormData();
fd.append('test', '123');

client.postForm('http://example.com', fd).catch(() => {});
