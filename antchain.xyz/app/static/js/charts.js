/**
 * Created by Administrator on 2017/2/11.
 */
$(document).ready(function () {
    // 基于准备好的dom，初始化echarts实例
    var mychart = echarts.init(document.getElementById('main'));
    var mychart1 = echarts.init(document.getElementById('haha'));
    var dzzz = echarts.init(document.getElementById('dizhizengzhang'))
    mychart.showLoading();
    mychart1.showLoading();
    // dzzz.showLoading();
    setInterval(function () {
        $.get('/chart_yaosu', function (result) {
            // 指定图表的配置项和数据
            var data = eval('(' + result + ')');
            var option = {
                title: {
                    text: '区块、交易对比图',
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: ['系统区块数量', '有效区块数量', '系统交易数量', '有效交易数量']
                },
                series: [{
                    name: 'antchain.xyz',
                    type: 'pie',
                    radius: '55%',
                    center: ['50%', '60%'],
                    data: [
                        {value: data.block_shu, name: '系统区块数量'},
                        {value: data.block_ne, name: '有效区块数量'},
                        {value: data.tx_shu, name: '系统交易数量'},
                        {value: data.tx_ne, name: '有效交易数量'},
                    ],
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }]
            };
            var option1 = {
                title: {
                    text: '小蚁系统内部资源',
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: ['系统地址数', '系统资产数', 'ANS持有人', 'ANC持有人']
                },
                series: [{
                    name: 'antchain.xyz',
                    type: 'pie',
                    radius: '55%',
                    center: ['50%', '60%'],
                    data: [
                        {value: data.address_shu, name: '系统地址数'},
                        {value: data.asset_shu, name: '系统资产数'},
                        {value: data.ans, name: 'ANS持有人'},
                        {value: data.anc, name: 'ANC持有人'},
                    ],
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }]
            };
            // 使用刚指定的配置项和数据显示图表。
            mychart.hideLoading();
            mychart1.hideLoading();
            mychart.setOption(option);
            mychart1.setOption(option1);
        });
    }, 3000);
    setInterval(function () {
        $.get('/dzzz', function (result) {
            // 指定图表的配置项和数据
            var data = eval('(' + result + ')');
            var option = {
                title: {
                    text: '区块、交易对比图',
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: ['系统区块数量', '有效区块数量', '系统交易数量', '有效交易数量']
                },
                series: [{
                    name: 'antchain.xyz',
                    type: 'pie',
                    radius: '55%',
                    center: ['50%', '60%'],
                    data: [
                        {value: data.block_shu, name: '系统区块数量'},
                        {value: data.block_ne, name: '有效区块数量'},
                        {value: data.tx_shu, name: '系统交易数量'},
                        {value: data.tx_ne, name: '有效交易数量'},
                    ],
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }]
            };
            // 使用刚指定的配置项和数据显示图表。
            // dzzz.hideLoading();
            dzzz.setOption(option);
        });
    }, 3000);
});
