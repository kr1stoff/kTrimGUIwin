# kTrimGUIwin
使用 `tkinter` 模块开发去引物软件，后台使用 `docker ubuntu` 环境安装分析需用软件。  
现已打包成可执行文件 `dist\wytrim.exe`

## 软件运行流程
1. 根据用户填写的 FASTQ 文件夹路径, 搜索路径下的所有 FASTQ, 返回可删除项目列表  
2. 迭代列表的 `FASTQ` 文件，先使用 `fastp` 去引物，在使用 `ktrim` 去引物
3. 生成结果文件，后缀为 `.trimmed.fq`

## 安装方法
1. 先安装docker, 拉镜像
```
docker pull kristoffmeng/mambaforge
```
2. 复制软件压缩包, 解压运行
