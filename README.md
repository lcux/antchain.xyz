# antchain.xyz
小蚁区块链浏览器

整个浏览器分为两个部分，一部分是数据入库程序，是通过python程序时刻与小蚁节点通信，通过节点提供的RPC功能，获取每一条区块的信息，然后进行数据处理并存入了mongodb数据库。另一部分是信息提供的角色，就是所谓的网站，我叫它数据出库程序。
数据入库程序由Python+Mongodb构成；数据出库程序由python+Flask+mongodb+bootstrap构成。
