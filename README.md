# Event-Mapping-Knowledge-Domain
- [Event-Mapping-Knowledge-Domain](#event-mapping-knowledge-domain)
  - [事件知识图谱](#事件知识图谱)
  - [数据集](#数据集)
  - [挂载地点](#挂载地点)
  - [构建流程](#构建流程)
  - [项目结构](#项目结构)

## 事件知识图谱

## schema

如下图所示：
![](./data/schema.png)

## 数据集

wikipedia

## 挂载地点

## 构建流程


---

## 项目结构

|文件夹|作用|
|:---:|:---:|
|`config`|连接neo4j数据库的配置，请自行创建，若是本小组成员，请向相关同学索取|
|`data`|爬取数据；制定`schema`；导出json格式数据|
|`merge`|指代消解；合并冗余实体|
|`infer`|知识计算，服务端的入口文件|