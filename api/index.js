const http = require('http');
const express = require('express');
const port = 42069;

//DEFINING THE APP

const app = express();
const timelineRoute = require('./routes/timeline')
const topRoute = require('./routes/top')
const statsRoute = require('./routes/stats')
const cors = require('cors')

app.use(cors({ origin: true }));
app.use('/timeline', timelineRoute);
app.use('/top', topRoute);
app.use('/stats', statsRoute);
module.exports = app;

const server = http.createServer(app);
server.listen(port);
