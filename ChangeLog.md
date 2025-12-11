


# [1.1.0] - 2025-12-10
### Change
- 支持读取项目外部的绝对路, 以便直接读取系统其他路径(Nas挂载磁盘)下文件的需求
- 在batch_runner_media_converter进行视频压缩时, 保持输出文件夹保持输入文件夹的目录结构

比如:
输入文件夹
 /1.mp4
 /serial2/2.mp4
 /collection3/serial3/3.mp4

输出文件夹
 /1.mp4
 /serial2/2.mp4
 /collection3/serial3/3.mp4