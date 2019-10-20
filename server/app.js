const express = require('express');
const app = express();
const body = require('body-parser');
const spiderRouter = require('./routers/spider');

//启动监听
let listen = 8080;
app.listen(listen, function (err) {
    if (err) throw err;
    console.info('服务器启动成功，端口：' + listen)
});

app.use(express.static('public'));//静态目录
//启用内置查询字符串功能
app.use(body.urlencoded({
    extended: false
}));

app.use('', spiderRouter);