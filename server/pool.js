const mysql = require('mysql');
//连接池对象
const pool = mysql.createPool({
    host:'127.0.0.1',
    prot:3306,
    user:'root',
    password:'',
    database:'samr',
    connectionLimit:20
});
//导出连接池对象
module.exports=pool;