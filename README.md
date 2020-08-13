# OMRON-FINS-Protocol-Attack
OMRON FINS Protocol analysis and attack script

## 1. FINS协议简介
欧姆龙(Omron)是来自日本的全球制造公司，产品是工业和制造业的机器。其中、小型PLC在国内市场有较高的占有率，有CJ、CM等系列。PLC可以支持Fins、Host link等协议进行通信。支持以太网的欧姆龙PLC CPU、以太网通信模块根据型号的不同，一般都会支持FINS(Factory Interface Network Service)协议，一些模块也会支持EtherNet/IP协议。

FINIS协议使用的TCP/UDP端口：9600

FINS协议使用的编码格式为：ASCII

Fins协议封装在TCP/UDP之上，FINS以太网协议基于OSI模型如下。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721112345364.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
## 2. FINS协议解析
### 2.1 FINS会话流程
FINS会话流程是基于TCP/IP协议，下图表述了FINS会话开始几个数据帧的作用。FINS协议的会话有一次请求帧，请求帧中附带着发起方的节点参数。PLC端（Server端）会确认并将自己的节点参数放回给请求方。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721113039560.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
### 2.2 FINS帧结构
FINS帧结构包含三部分组成，分别由FINS Header、FINS Command Code和FINS Command Data组成。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721114452401.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70#pic_center)
### 2.3 FINS Header
#### 2.3.1 FINS/TCP Header
Magic Bytes(4 bytes)：0x46494e53(Protocol ID，协议ID，FINS的16进制ASCII码)

Length(4 bytes): 数据长度，指后续跟着的字符长度

Reserved(3 bytes):保留，通常为0x000000

Command Type(1 byte):数据帧类型，值如下：

 - 0x00：connect requst 连接请求数据帧
 - 0x01：connect Response，连接请求确认数据；
 - 0x02：data，数据传输；
 
 Error Code(4 bytes)：保留，通常为0x00000000
 ![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721120731632.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)

#### 2.3.2 FINS Header

0：ICF(1 byte)：（Information Control Field）信息控制码：

- 由4个子字段组成，分述如下：
- 1… …. = Gateway bit，是否使用网关，0x01表示使用；
- .1.. …. = Data Type bit，数据类型比特位，0x01表示为响应，0x00表示命令；
- ..0. …. = Reserved bit，第一个保留比特位，默认置0；
- …0 …. = Reserved bit，第二个保留比特位，默认置0；
- …. 0… = Reserved bit，第三个保留比特位，默认置0；
- …. .0.. = Reserved bit，第四个保留比特位，默认置0；
- …. ..0. = Reserved bit，第五个保留比特位，默认置0；
- …. …1 = Response setting bit，第一个保留比特位响应标志为，0x01表示非必需回应，0x00表示必须进行回应。

1：Rev(1 byte)：（Reserved）预留 一般为0x00。

2：GCT(1 byte)：（Gateway count）网关数量，一般为0x02。

3：DNA(1 byte)：（Destination network address）目标网络地址。

- 00：本地网络
- 01 to 7F：远程网络

4：DA1(1 byte)：（Destination node number）目标节点号。

- 01 to 7E：SYSMAC NET 网络节点号
- 01 to 3E：SYSMAC LINK 网络节点号
- FF：广播节点号

5：DA2(1 byte)：（Source unit number）源单元号。

- 00：PC（CPU）
- FE：SYSMAC NET连接单元或者SYSMAC LINK单元连接网络
- 10 to 1F：CPU 总线单元

6：SNA(1 byte)：（Source network address）源网络地址。

- 00：本地网络
- 01 to 7F：远程网络

7：SA1(1 byte)：（Source node number）源节点号

- 01 to 7E：SYSMAC NET 网络节点号
- 01 to 3E：SYSMAC LINK 网络节点号
- FF：广播节点号

8：SA2(1 byte)：（Source Unit address）源单元地址

- 00：PC（CPU）
- FE：SYSMAC NET连接单元或者SYSMAC LINK单元连接网络
- 10 to 1F：CPU 总线单元

9：SID(1 byte)：（Service ID） 序列号 范围00-FF

10～11：Commands code(2 byte)：命令码，分为一级命令码和二级命令码。详细的命令码可参考FINS Commands code。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721120951213.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
## 3. Command
### 3.1 Client/Server Node Address 建立连接
这两个字段是Fins/TCP的客户端/服务器建立连接的时候的类似DHCP协议客户端获取IP地址的时候才会出现的，如下所示：

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721150813980.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
Fins/TCP协议的客户端/服务器在传输有效的命令数据之前，由客户端先向服务器发送一个包含Client Node Address字段的报文申请节点地址,类似DHCP协议，由于客户端申请的时候还没有节点地址，因此该字段被置为0x00000000，如下图所示：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721150939249.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
服务器收到客户端请求后，给客户端分配相应的节点地址并通告给客户端，同时在报文中包含服务器自己的节点地址信息，如下所示：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721151116769.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
客户端收到服务器的响应报文后，即使用分配的节点地址与服务器进行通信，由此客户端/服务器之间就建立起了有效的长连接。

### 3.2 操作模式切换：RUN/MONITOR/STOP/RESET
PLC模式切换
![在这里插入图片描述](https://img-blog.csdnimg.cn/2020072115430755.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
Commands Code：
功能码，0x0401

Program No.：
程序码，一般为0xFFFF

Mode：
模式
- Monitor模式 0x02
- Run模式 0x04

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721154336289.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
STOP模式：

- Command Code：功能码，0x0402
- Program No.：程序码，一般为0xFFFF

RESET模式：

- Command Code：功能码，0x0403
- Program No.：程序码，一般为0xFFFF

### 3.3 强制设置&取消强制设置
Forced功能码可以强制设置或者强制重置位。也可以强制设置状态及释放状态。在恢复强制状态前，程序将无法继续执行。

#### 3.3.1 强制设置
其命令结构如下图所示。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721154937127.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
Commands Code：功能码，0x2301

No.of bits/flags：位号。

Force Set/Reset data：强制/置位数据。

- Set/Reset Designation：执行动作。
	- 0x0000：强制复位
	- 0x0001：强制置位
	- 0x8000：强制释放并复位
	- 0x8001：强制释放并置位
	- 0xFFFF：解除强制状态

Memory Area Code：存储区域代码，需要根据PLC型号而定

Bit/Flags：位/状态设置

#### 3.3.2 取消强制设置
Command Code:0x2302
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721155637747.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
### 3.4 读取/写入 IO Memory Area
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721160637660.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)

#### 3.4.1 读取 IO Memory Area
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721160158618.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
Command Code：0x0101

IO Memory area code：IO存储区代码

Beginning address：起始地址

No of items（二进制）：0～15

#### 3.4.2 写入 IO Memory Area
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721160812811.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
Command Code：0x0102

IO Memory area code：IO存储区代码

Beginning address：起始地址

No of items（二进制）：0～15

Data：要写入的数据

> 记得根据data长度改fins/tcp header里的包长度

#### 3.4.3 填充 IO Memory Area
使用相同数据填充IO Memory Area
![在这里插入图片描述](https://img-blog.csdnimg.cn/2020072116134664.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
Command Code：0x0103

IO Memory area code：IO存储区代码

Beginning address：起始地址

No of items（二进制）：0～15

Data：要填充的数据

### 3.5 非专用IO存储区
非专用IO存储区：Parameter Area、Program Area

#### 3.5.1 读取 Parameter Area
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721161754962.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
#### 3.5.1 读取 Program Area
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721161906120.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
### 3.6 读取/写入/删除单个文件
#### 3.6.1 读取单个文件
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721162019311.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)

Command Code：0x2202

Disk No：磁盘号
- 0x8000：Memory Card
- 0x8001:  EM flie memory 

File name：最大长度12bytes，值为16进制的ascii码，缺的后面补0x00

File position：起始的byte adress，文件开始于0x00000000

Data length：要读的数据长度

Directory length：文件所在目录名称长度包括\，0x0000为默认根目录

Absolute Directory path：最长65个字，开始于\（0x5c）

> 记得根据data长度改fins/tcp header里的包长度

#### 3.6.2 写入单个文件
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721163224950.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
Command Code：0x2203

Disk No：磁盘号
- 0x8000：Memory Card
- 0x8001:  EM flie memory 

File name：最大长度12bytes，值为16进制的ascii码，缺的后面补0x00

File position：起始的byte adress，文件开始于0x00000000

Data length：要读的数据长度

File data：要写入的文件数据，值为16进制的ascii码

Directory length：文件所在目录名称长度包括\，0x0000为默认根目录

Absolute Directory path：最长65个字，开始于\（0x5c）

> 记得根据data长度改fins/tcp header里的包长度

#### 3.6.3 删除文件
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200721163436152.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyNTA1MjA3,size_16,color_FFFFFF,t_70)
Command Code：0x2202

Disk No：磁盘号
- 0x8000：Memory Card
- 0x8001:  EM flie memory 

No of files：指定要删除的文件数量，单个写0x0001即可

File name：最大长度12bytes，值为16进制的ascii码，缺的后面补0x00

Directory length：文件所在目录名称长度包括\，0x0000为默认根目录

Absolute Directory path：最长65个字，开始于\（0x5c）
