//爬虫路由器模块
const express = require('express');
//路由器对象
const router = express.Router();
//导入mysql连接池模块
const pool = require('../pool');
var exec = require('child_process').exec;

//启动爬虫模块
router.post('/spider', function (req, res) {
    // let qt = req.params.qt;
    let data = req.body;
    let qt = data.qt;
    let batchNumber=data.batchNumber;
    let beginTime=data.beginTime;
    res.send({"msg":"爬虫启动成功"});
    console.log(data);
    exec('python E:\\samr/begin.py '+qt+' '+beginTime+' '+batchNumber,function(error,stdout,stderr){
        if(stdout.length >1){
            console.log('you offer args:',stdout);
            let sql="update info set flag=? where batchNumber=?";
            pool.query(sql,[1,batchNumber],function (err,result) {
                if (err) throw err;
                if (result.affectedRows>0){
                    console.log('数据库修改成功')
                }else {
                    console.log('数据库修改失败')
                }
            })
        } else {
            console.log('you don\'t offer args');
        }
        if(error) {
            console.info('stderr : '+stderr);
        }
    });

});

//获得info列表
router.post('/info',function (req,res) {
    sql="select * from info order by id desc";
    pool.query(sql,function (err,result) {
        if (err) throw err;
        res.send(result)
    })
});

//导出模块
module.exports = router;